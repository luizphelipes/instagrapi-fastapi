#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados PostgreSQL.
Execute este script para verificar se a configuração está correta.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

async def test_database_connection():
    """Testa a conexão com o banco de dados"""
    
    # Obtém a URL do banco de dados
    database_url = os.getenv(
        'DATABASE_URL', 
        'postgresql+asyncpg://user:password@localhost:5432/instagram_api'
    )
    
    print(f"🔍 Testando conexão com: {database_url}")
    
    try:
        # Cria o engine
        engine = create_async_engine(
            database_url,
            echo=True,  # Mostra as queries SQL
            pool_pre_ping=True,
            pool_recycle=300,
            future=True,
            connect_args={
                "server_settings": {
                    "application_name": "instagram_api_test"
                }
            }
        )
        
        print("✅ Engine criado com sucesso")
        
        # Testa a conexão
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
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