#!/usr/bin/env python3
"""
Script para criar as tabelas do banco de dados manualmente.
Execute este script se as tabelas não forem criadas automaticamente.
"""

import asyncio
import os
from dotenv import load_dotenv
from database import engine, Base

load_dotenv()

async def create_tables():
    """Cria todas as tabelas definidas nos modelos"""
    
    print("🚀 Iniciando criação das tabelas...")
    
    try:
        async with engine.begin() as conn:
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
            else:
                print("❌ Tabela instagram_accounts não foi criada!")
                
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    
    return True

async def main():
    """Função principal"""
    print("🔧 Script de criação de tabelas")
    print("=" * 50)
    
    success = await create_tables()
    
    if success:
        print("🎉 Tabelas criadas com sucesso!")
    else:
        print("💥 Falha ao criar tabelas!")
        print("\n🔧 Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Verifique se as credenciais estão corretas")
        print("3. Verifique se o banco de dados existe")
        print("4. Verifique se o usuário tem permissões para criar tabelas")

if __name__ == "__main__":
    asyncio.run(main()) 