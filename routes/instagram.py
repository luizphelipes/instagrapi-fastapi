from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import httpx
from urllib.parse import quote

from database import get_db, InstagramAccount
from services.instagram_service import get_instagram_service
from services.redis_cache import get_cache_stats, clear_cache_pattern
from schemas import (
    LoginRequest, LoginResponse, AccountsListResponse, ProfileResponse,
    StoriesResponse, PostsResponse, ReelsResponse, PrivacyResponse
)

instagram_router = APIRouter()

@instagram_router.get("/accounts", response_model=AccountsListResponse)
async def list_accounts(db: AsyncSession = Depends(get_db)):
    """Lista todas as contas salvas no banco de dados."""
    service = await get_instagram_service()
    accounts_data = await service.list_accounts(db)
    return {
        "status": "success",
        "accounts": accounts_data
    }

@instagram_router.delete("/accounts/{username}")
async def delete_account(username: str, db: AsyncSession = Depends(get_db)):
    """Deleta uma conta específica."""
    service = await get_instagram_service()
    if await service.delete_account(username, db):
        return {"status": "success", "message": f"Account {username} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail=f"Account {username} not found.")

@instagram_router.post("/auth/login-by-session", response_model=LoginResponse)
async def login_by_session(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Realiza o login a partir de um session_id do Instagram, valida a conta e a salva no banco de dados.
    """
    service = await get_instagram_service()
    result = await service.login_and_save_account_by_session(request.session_id, db)

    if result['status'] == 'success':
        return result
    else:
        # Retorna 401 para sessão inválida, 500 para outros erros
        status_code = 401 if "invalid" in result.get('message', '').lower() else 500
        raise HTTPException(status_code=status_code, detail=result['message'])

@instagram_router.get("/users/{username}/stories", response_model=StoriesResponse)
async def get_user_stories(username: str, db: AsyncSession = Depends(get_db)):
    """Obtém os stories de um usuário."""
    service = await get_instagram_service()
    result = await service.get_user_stories(username, db)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['message'])
    
    return result

@instagram_router.get("/users/{username}", response_model=ProfileResponse)
async def get_profile_info(username: str, db: AsyncSession = Depends(get_db)):
    """
    Obtém informações detalhadas de um perfil do Instagram.
    Agora retorna o URL da foto de perfil já passando pelo proxy-image, incluindo o domínio completo.
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    service = await get_instagram_service()
    result = await service.get_profile_info(username, db)

    if result['status'] == 'error':
        status_code = 404 if "not found" in result.get("message", "") else 500
        raise HTTPException(status_code=status_code, detail=result.get("message"))
    
    data = result.get("data")
    if data and data.get("profile_pic_url"):
        # Adiciona o domínio completo antes do endpoint
        proxy_url = f"https://insta-api.gfollow.store/api/v1/proxy-image?url={quote(data['profile_pic_url'])}"
        data["profile_pic_proxy_url"] = proxy_url
    
    return {"success": True, "data": data}

@instagram_router.get("/users/{username}/privacy", response_model=PrivacyResponse)
async def check_user_privacy(username: str, db: AsyncSession = Depends(get_db)):
    """
    Verifica a privacidade de um perfil do Instagram.
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    service = await get_instagram_service()
    result = await service.get_profile_privacy(username, db)

    if result['status'] == 'error':
        status_code = 404 if "not found" in result.get("message", "") else 500
        raise HTTPException(status_code=status_code, detail=result.get("message"))
    
    return result

@instagram_router.get("/users/{username}/posts", response_model=PostsResponse)
async def get_user_posts(
    username: str, 
    count: int = Query(4, ge=1, le=12),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém os últimos posts de um usuário do Instagram.
    Aceita um parâmetro 'count' na query string (padrão: 4).
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    service = await get_instagram_service()
    result = await service.get_last_posts(username, count, db)

    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['message'])
    
    return result

@instagram_router.get("/users/{username}/reels", response_model=ReelsResponse)
async def get_user_reels(
    username: str, 
    count: int = Query(4, ge=1, le=12),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém os últimos reels de um usuário do Instagram.
    Aceita um parâmetro 'count' na query string (padrão: 4).
    """
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    service = await get_instagram_service()
    result = await service.get_last_reels(username, count, db)

    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['message'])
    
    return result

@instagram_router.get("/proxy-image")
async def proxy_image(url: str):
    """
    Proxy para imagens externas (solução para CORS).
    Recebe a URL da imagem via query string e retorna o conteúdo da imagem.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            
            return StreamingResponse(
                iter([response.content]),
                media_type=content_type
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to fetch image: {str(e)}')

@instagram_router.get("/accounts/status")
async def get_accounts_status():
    """Retorna status detalhado de todas as contas e sistema de pré-aquecimento"""
    service = await get_instagram_service()
    return await service.get_accounts_status()

@instagram_router.get("/accounts/{username}/status")
async def get_account_status(username: str):
    """Retorna status detalhado de uma conta específica"""
    service = await get_instagram_service()
    return await service.get_account_status(username)

@instagram_router.post("/accounts/{username}/warmup/start")
async def start_account_warmup(username: str):
    """Inicia pré-aquecimento para uma conta específica"""
    service = await get_instagram_service()
    await service.start_account_warmup(username)
    return {"status": "success", "message": f"Pré-aquecimento iniciado para conta {username}"}

@instagram_router.post("/accounts/{username}/warmup/stop")
async def stop_account_warmup(username: str):
    """Para pré-aquecimento de uma conta específica"""
    service = await get_instagram_service()
    await service.stop_account_warmup(username)
    return {"status": "success", "message": f"Pré-aquecimento parado para conta {username}"}

@instagram_router.post("/warmup/system/stop")
async def stop_warmup_system():
    """Para o sistema de pré-aquecimento completo"""
    service = await get_instagram_service()
    await service.stop_warmup_system()
    return {"status": "success", "message": "Sistema de pré-aquecimento parado"}

@instagram_router.get("/warmup/logs")
async def get_warmup_logs(limit: int = Query(100, ge=1, le=1000)):
    """Retorna logs detalhados do sistema de pré-aquecimento"""
    service = await get_instagram_service()
    logs = await service.get_warmup_logs(limit)
    
    return {
        "status": "success",
        "total_logs": len(logs),
        "requested_limit": limit,
        "logs": logs
    }

@instagram_router.get("/cache/stats")
async def get_cache_stats_route():
    """Retorna estatísticas do cache Redis"""
    return await get_cache_stats()

@instagram_router.delete("/cache/clear")
async def clear_cache_route(pattern: str = "*"):
    """Limpa cache baseado em padrão"""
    success = await clear_cache_pattern(pattern)
    if success:
        return {"status": "success", "message": f"Cache cleared for pattern: {pattern}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear cache") 