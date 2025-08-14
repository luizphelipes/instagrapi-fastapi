#!/usr/bin/env python3
"""
Script para verificar as dependências instaladas.
Execute este script para verificar se todas as dependências estão corretas.
"""

import sys
import importlib

def check_dependency(module_name, package_name=None):
    """Verifica se uma dependência está instalada"""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'N/A')
        print(f"✅ {module_name} - Versão: {version}")
        return True
    except ImportError:
        print(f"❌ {module_name} - NÃO INSTALADO")
        if package_name:
            print(f"   💡 Instale com: pip install {package_name}")
        return False

def main():
    """Função principal"""
    print("🔍 Verificando dependências...")
    print("=" * 50)
    
    # Dependências principais
    dependencies = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn[standard]"),
        ("sqlalchemy", "sqlalchemy"),
        ("asyncpg", "asyncpg"),
        ("redis", "redis"),
        ("instagrapi", "instagrapi"),
        ("python-dotenv", "python-dotenv"),
        ("cryptography", "cryptography"),
        ("pydantic", "pydantic"),
        ("PIL", "Pillow"),
        ("httpx", "httpx"),
    ]
    
    all_ok = True
    
    for module_name, package_name in dependencies:
        if not check_dependency(module_name, package_name):
            all_ok = False
    
    print("=" * 50)
    
    # Verifica se psycopg2 está instalado (não deve estar)
    try:
        import psycopg2
        print(f"⚠️  psycopg2 está instalado - Versão: {psycopg2.__version__}")
        print("   💡 Recomendado: pip uninstall psycopg2-binary")
        all_ok = False
    except ImportError:
        print("✅ psycopg2 - NÃO INSTALADO (correto)")
    
    print("=" * 50)
    
    # Testa importação do SQLAlchemy async
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        print("✅ SQLAlchemy async - OK")
    except ImportError as e:
        print(f"❌ SQLAlchemy async - Erro: {e}")
        all_ok = False
    
    # Testa importação do asyncpg
    try:
        import asyncpg
        print(f"✅ asyncpg - Versão: {asyncpg.__version__}")
    except ImportError as e:
        print(f"❌ asyncpg - Erro: {e}")
        all_ok = False
    
    print("=" * 50)
    
    if all_ok:
        print("🎉 Todas as dependências estão corretas!")
    else:
        print("💥 Algumas dependências estão faltando ou incorretas.")
        print("\n🔧 Para corrigir:")
        print("1. Execute: pip install -r requirements.txt")
        print("2. Se psycopg2 estiver instalado: pip uninstall psycopg2-binary")
        print("3. Reconstrua o container: docker-compose build --no-cache")

if __name__ == "__main__":
    main() 