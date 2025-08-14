import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn
from sqlalchemy import text

from database import engine, Base
from routes.instagram import instagram_router
from services.redis_cache import init_redis

# Carrega variáveis de ambiente
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para inicialização e limpeza da aplicação"""
    # Inicializa o banco de dados
    try:
        async with engine.begin() as conn:
            # Verifica se as tabelas já existem
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'instagram_accounts')")
            )
            table_exists = result.scalar()
            
            if not table_exists:
                print("📋 Tabela instagram_accounts não encontrada. Criando tabelas...")
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Tabelas criadas com sucesso")
            else:
                print("✅ Tabelas já existem, pulando criação")
    except Exception as e:
        print(f"⚠️ Aviso: Erro ao verificar/criar tabelas: {e}")
        print("🔄 Tentando criar tabelas diretamente...")
        
        # Tenta criar as tabelas diretamente
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Tabelas criadas com sucesso na segunda tentativa")
        except Exception as e2:
            print(f"❌ Erro ao criar tabelas na segunda tentativa: {e2}")
            print("⚠️ Continuando com a inicialização...")
    
    # Inicializa conexão Redis
    await init_redis()
    
    yield
    
    # Cleanup
    await engine.dispose()

# Cria a aplicação FastAPI
app = FastAPI(
    title="Instagram API - FastAPI Version",
    description="API wrapper para Instagram usando FastAPI e Instagrapi",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure conforme necessário em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os roteadores
app.include_router(instagram_router, prefix="/api/v1", tags=["instagram"])

@app.get("/", tags=["health"])
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "message": "Instagram API FastAPI is running",
        "version": "2.0.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 