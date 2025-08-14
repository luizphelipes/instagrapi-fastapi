import redis.asyncio as redis
import os
import json
from functools import wraps
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

# Configuração Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_password = os.getenv("REDIS_PASSWORD", None)

# Cliente Redis global
redis_client: redis.Redis = None

async def init_redis():
    """Inicializa conexão Redis com configurações otimizadas para performance"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=3,  # Reduzido de 5 para 3
            socket_timeout=3,          # Reduzido de 5 para 3
            retry_on_timeout=True,
            health_check_interval=30,
            max_connections=20,        # Aumenta pool de conexões
            socket_keepalive=True,     # Mantém conexões ativas
            socket_keepalive_options={},
        )
        # Testa conexão
        await redis_client.ping()
        logger.info("Redis connection established successfully with optimized settings")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None

async def get_redis():
    """Retorna cliente Redis ou None se não disponível"""
    if redis_client is None:
        await init_redis()
    return redis_client

def redis_cache(ttl: int):
    """
    Decorator para cachear o resultado de uma função no Redis por um tempo (ttl) em segundos.
    Versão otimizada para melhor performance.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Cria uma chave de cache estável, ignorando o parâmetro db
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'db'}
            key_parts = [func.__name__] + list(args[1:]) + [f"{k}={v}" for k, v in sorted(filtered_kwargs.items())]
            cache_key = ":".join(map(str, key_parts))
            
            try:
                redis_conn = await get_redis()
                if redis_conn is None:
                    # Se Redis não disponível, executa função sem cache
                    return await func(*args, **kwargs)
                
                # 1. Tenta obter o resultado do cache com timeout reduzido
                cached_result = await redis_conn.get(cache_key)
                if cached_result:
                    logger.debug(f"Cache HIT for key: {cache_key}")
                    return json.loads(cached_result)
                
                # 2. Se não estiver no cache, executa a função
                logger.debug(f"Cache MISS for key: {cache_key}")
                result = await func(*args, **kwargs)
                
                # 3. Armazena o resultado no cache apenas se for bem-sucedido
                # Usa pipeline para melhor performance
                if isinstance(result, dict) and result.get("status") == "success":
                    pipe = redis_conn.pipeline()
                    pipe.setex(cache_key, ttl, json.dumps(result))
                    await pipe.execute()
                
                return result
                
            except Exception as e:
                logger.error(f"Redis cache error: {e}. Bypassing cache.")
                # Em caso de erro, executa a função original sem cache
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

async def clear_cache_pattern(pattern: str) -> bool:
    """Limpa cache baseado em padrão"""
    try:
        redis_conn = await get_redis()
        if redis_conn is None:
            return False
        
        keys = await redis_conn.keys(pattern)
        if keys:
            await redis_conn.delete(*keys)
            logger.info(f"Cleared {len(keys)} cache keys matching pattern: {pattern}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return False

async def get_cache_stats() -> dict:
    """Retorna estatísticas do cache"""
    try:
        redis_conn = await get_redis()
        if redis_conn is None:
            return {"status": "error", "message": "Redis not available"}
        
        info = await redis_conn.info()
        return {
            "status": "success",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"status": "error", "message": str(e)} 