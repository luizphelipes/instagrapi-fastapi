#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados PostgreSQL.
Execute este script para verificar se a configuração está correta.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def test_database_connection():
    """Testa a conexão com o banco de dados"""
    
    # Obtém a URL do banco de dados
    database_url = os.getenv(
        'DATABASE_URL', 
        'postgresql+asyncpg://user:password@localhost:5432/instagram_api'
    )
    
    # Remove sslmode da URL e configura via connect_args
    ssl_mode = None
    if '?sslmode=' in database_url:
        # Extrai o sslmode da URL
        base_url, ssl_param = database_url.split('?sslmode=', 1)
        if '&' in ssl_param:
            ssl_param, rest = ssl_param.split('&', 1)
            database_url = base_url + '?' + rest
        else:
            database_url = base_url
        ssl_mode = ssl_param
    
    print(f"🔍 Testando conexão com: {database_url}")
    if ssl_mode:
        print(f"🔒 SSL Mode: {ssl_mode}")
    
    try:
        # Configura connect_args baseado no ssl_mode
        connect_args = {
            "server_settings": {
                "application_name": "instagram_api_test"
            }
        }
        
        # Configura SSL se necessário
        if ssl_mode == "disable":
            connect_args["ssl"] = False
        elif ssl_mode:
            connect_args["ssl"] = True
        
        # Cria o engine
        engine = create_async_engine(
            database_url,
            echo=True,  # Mostra as queries SQL
            pool_pre_ping=True,
            pool_recycle=300,
            future=True,
            connect_args=connect_args
        )
        
        print("✅ Engine criado com sucesso")
        
        # Testa a conexão
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conexão bem-sucedida!")
            print(f"📋 Versão do PostgreSQL: {version}")
        
        # Fecha o engine
        await engine.dispose()
        print("✅ Engine fechado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        return False
    
    return True

async def main():
    """Função principal"""
    print("🚀 Iniciando teste de conexão com banco de dados...")
    
    success = await test_database_connection()
    
    if success:
        print("🎉 Teste concluído com sucesso!")
    else:
        print("💥 Teste falhou!")
        print("\n🔧 Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Verifique se as credenciais estão corretas")
        print("3. Verifique se o banco de dados existe")
        print("4. Verifique se o asyncpg está instalado: pip install asyncpg")

if __name__ == "__main__":
    asyncio.run(main()) 