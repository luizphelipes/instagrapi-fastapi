#!/usr/bin/env python3
"""
Script de inicialização para desenvolvimento da API Instagram FastAPI
"""
import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Inicializa a aplicação em modo desenvolvimento"""
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configurações de desenvolvimento
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"🚀 Iniciando Instagram API FastAPI em modo desenvolvimento...")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"📚 Documentação: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    print(f"💚 Health Check: http://{host}:{port}/")
    print("=" * 50)
    
    # Inicia o servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 