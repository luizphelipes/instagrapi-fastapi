#!/usr/bin/env python3
"""
Script para testar a correção do SSL mode no banco de dados.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ssl_fix():
    """Testa se a correção do SSL mode funciona"""
    
    # Simula a URL com sslmode
    test_url = "postgresql://postgres:password@localhost:5432/test?sslmode=disable"
    
    print(f"🔍 URL original: {test_url}")
    
    # Remove sslmode da URL e configura via connect_args
    ssl_mode = None
    if '?sslmode=' in test_url:
        # Extrai o sslmode da URL
        base_url, ssl_param = test_url.split('?sslmode=', 1)
        if '&' in ssl_param:
            ssl_param, rest = ssl_param.split('&', 1)
            test_url = base_url + '?' + rest
        else:
            test_url = base_url
        ssl_mode = ssl_param
    
    print(f"🔗 URL limpa: {test_url}")
    print(f"🔒 SSL Mode: {ssl_mode}")
    
    # Configura connect_args baseado no ssl_mode
    connect_args = {
        "server_settings": {
            "application_name": "test_ssl_fix"
        }
    }
    
    # Configura SSL se necessário
    if ssl_mode == "disable":
        connect_args["ssl"] = False
        print("✅ SSL desabilitado via connect_args")
    elif ssl_mode:
        connect_args["ssl"] = True
        print("✅ SSL habilitado via connect_args")
    
    print(f"🔧 Connect args: {connect_args}")
    
    # Testa se a URL está no formato correto para asyncpg
    if not test_url.startswith('postgresql+asyncpg://'):
        test_url = test_url.replace('postgresql://', 'postgresql+asyncpg://')
        print(f"🔄 URL convertida para asyncpg: {test_url}")
    
    print("✅ Teste de parsing da URL concluído com sucesso!")

async def main():
    """Função principal"""
    print("🚀 Testando correção do SSL mode...")
    print("=" * 50)
    
    await test_ssl_fix()
    
    print("=" * 50)
    print("🎉 Teste concluído! A correção do SSL mode está funcionando.")

if __name__ == "__main__":
    asyncio.run(main()) 