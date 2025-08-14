#!/usr/bin/env python3
"""
Script de pré-aquecimento do serviço Instagram.
Execute este script para inicializar o serviço e reduzir cold start.
"""

import asyncio
import os
import time
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

from services.instagram_service import InstagramService
from database import get_db

async def prewarm_service():
    """Pré-aquece o serviço Instagram"""
    
    print("🔥 Iniciando pré-aquecimento do serviço Instagram...")
    start_time = time.time()
    
    try:
        # Cria instância do serviço
        service = InstagramService()
        
        # Inicializa o serviço
        await service.initialize()
        
        # Testa uma consulta simples para aquecer o cache
        print("🧪 Testando consulta de exemplo...")
        
        # Simula uma consulta de perfil (será cacheada)
        test_username = "instagram"  # Usuário público conhecido
        result = await service.get_profile_privacy(test_username)
        
        if result.get("status") == "success":
            print(f"✅ Consulta de teste bem-sucedida: {result}")
        else:
            print(f"⚠️ Consulta de teste falhou: {result}")
        
        # Aguarda um pouco para estabilizar
        await asyncio.sleep(2)
        
        total_time = time.time() - start_time
        print(f"🎉 Pré-aquecimento concluído em {total_time:.2f}s")
        
        # Mostra status das contas
        accounts_status = service.account_manager.get_all_accounts_status()
        print(f"📊 Status das contas: {accounts_status['total_accounts']} total, {accounts_status['active_accounts']} ativas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no pré-aquecimento: {e}")
        return False

async def main():
    """Função principal"""
    print("🚀 Script de Pré-aquecimento do Instagram Service")
    print("=" * 60)
    
    success = await prewarm_service()
    
    if success:
        print("✅ Pré-aquecimento concluído com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. O serviço está pronto para receber requisições")
        print("2. Cold start deve ser significativamente reduzido")
        print("3. Cache está ativo e funcionando")
    else:
        print("💥 Pré-aquecimento falhou!")
        print("\n🔧 Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Verifique se o Redis está disponível")
        print("3. Verifique se as session IDs estão configuradas")

if __name__ == "__main__":
    asyncio.run(main()) 