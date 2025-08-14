#!/usr/bin/env python3
"""
Script de inicialização do banco de dados para EasyPanel.
Este script é executado dentro do container para configurar o banco de dados.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório atual ao path
sys.path.append('/app')

# Configura as variáveis de ambiente para EasyPanel se não estiverem definidas
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = "postgresql://postgres:d30bfb311dd156dad365@servidor_fastapi-postgres:5432/servidor"

if not os.getenv('REDIS_HOST'):
    os.environ['REDIS_HOST'] = "servidor_fastapi-redis"

if not os.getenv('REDIS_PORT'):
    os.environ['REDIS_PORT'] = "6379"

if not os.getenv('REDIS_PASSWORD'):
    os.environ['REDIS_PASSWORD'] = "14c652679ebd921579d6"

# Gera uma chave de criptografia se não existir
if not os.getenv('ENCRYPTION_KEY'):
    from cryptography.fernet import Fernet
    encryption_key = Fernet.generate_key().decode()
    os.environ['ENCRYPTION_KEY'] = encryption_key
    print(f"🔑 Nova chave de criptografia gerada: {encryption_key}")

load_dotenv()

# Importa após configurar as variáveis de ambiente
from database import engine, Base

async def wait_for_database(max_retries=60, delay=2):
    """Aguarda o banco de dados ficar disponível"""
    print("⏳ Aguardando banco de dados ficar disponível...")
    print(f"🔗 Tentando conectar em: {os.getenv('DATABASE_URL')}")
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
                print(f"✅ Banco de dados disponível na tentativa {attempt + 1}")
                return True
        except Exception as e:
            print(f"⏳ Tentativa {attempt + 1}/{max_retries}: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
    
    print("❌ Banco de dados não ficou disponível após todas as tentativas")
    return False

async def check_table_exists():
    """Verifica se a tabela já existe"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'instagram_accounts')"
            )
            table_exists = result.scalar()
            return table_exists
    except Exception as e:
        print(f"⚠️ Erro ao verificar tabela: {e}")
        return False

async def create_tables():
    """Cria todas as tabelas definidas nos modelos"""
    
    print("🚀 Iniciando criação das tabelas...")
    print(f"🔗 Conectando ao banco: {os.getenv('DATABASE_URL')}")
    
    # Verifica se a tabela já existe
    table_exists = await check_table_exists()
    if table_exists:
        print("✅ Tabela instagram_accounts já existe!")
        return True
    
    try:
        async with engine.begin() as conn:
            print("📋 Criando tabelas...")
            # Cria todas as tabelas
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tabelas criadas com sucesso!")
            
            # Verifica se a tabela foi criada
            result = await conn.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'instagram_accounts')"
            )
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Tabela instagram_accounts confirmada!")
                
                # Lista todas as tabelas criadas
                result = await conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
                tables = result.fetchall()
                print(f"📋 Tabelas no banco: {[table[0] for table in tables]}")
            else:
                print("❌ Tabela instagram_accounts não foi criada!")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        print(f"🔍 Tipo do erro: {type(e).__name__}")
        return False
    
    return True

async def main():
    """Função principal"""
    print("🔧 Inicialização do banco de dados")
    print("=" * 50)
    
    # Aguarda o banco de dados ficar disponível
    if not await wait_for_database():
        print("💥 Falha ao conectar com o banco de dados!")
        print("⚠️ Tentando continuar mesmo assim...")
    
    # Cria as tabelas
    success = await create_tables()
    
    if success:
        print("🎉 Inicialização do banco de dados concluída com sucesso!")
        return True
    else:
        print("💥 Falha ao criar tabelas!")
        print("⚠️ A aplicação será iniciada mesmo assim...")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            print("⚠️ Saindo com código de erro, mas a aplicação continuará...")
            sys.exit(0)  # Não falha completamente
    except Exception as e:
        print(f"❌ Erro crítico na inicialização: {e}")
        print("⚠️ Continuando com a inicialização da aplicação...")
        sys.exit(0)  # Não falha completamente 