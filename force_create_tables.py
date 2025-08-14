#!/usr/bin/env python3
"""
Script para forçar a criação das tabelas do banco de dados.
Execute este script manualmente se as tabelas não forem criadas automaticamente.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Configura as variáveis de ambiente para EasyPanel
os.environ['DATABASE_URL'] = "postgresql://postgres:d30bfb311dd156dad365@servidor_fastapi-postgres:5432/servidor"
os.environ['REDIS_HOST'] = "servidor_fastapi-redis"
os.environ['REDIS_PORT'] = "6379"
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

async def force_create_tables():
    """Força a criação das tabelas"""
    
    print("🚀 Forçando criação das tabelas...")
    print(f"🔗 Conectando ao banco: {os.getenv('DATABASE_URL')}")
    
    try:
        # Tenta conectar e criar as tabelas
        async with engine.begin() as conn:
            print("📋 Criando tabelas...")
            
            # Força a criação de todas as tabelas
            await conn.run_sync(Base.metadata.drop_all)  # Remove tabelas existentes
            print("🗑️ Tabelas existentes removidas")
            
            await conn.run_sync(Base.metadata.create_all)  # Cria novas tabelas
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
                
                # Testa uma inserção simples
                from database import InstagramAccount
                test_account = InstagramAccount(
                    username="test_user",
                    session_id="test_session"
                )
                await conn.commit()
                print("✅ Teste de inserção bem-sucedido!")
                
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
    print("🔧 Forçar criação de tabelas")
    print("=" * 50)
    
    success = await force_create_tables()
    
    if success:
        print("🎉 Tabelas criadas com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Reinicie a aplicação")
        print("2. Teste a API em: http://seu-dominio/api/v1/accounts")
    else:
        print("💥 Falha ao criar tabelas!")
        print("\n🔧 Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Verifique se as credenciais estão corretas")
        print("3. Verifique se o banco de dados existe")

if __name__ == "__main__":
    asyncio.run(main()) 