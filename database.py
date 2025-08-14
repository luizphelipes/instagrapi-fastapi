import os
import base64
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from datetime import datetime
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

# Configuração do banco de dados
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql+asyncpg://user:password@localhost:5432/instagram_api'
)

def generate_fernet_key():
    """Gera uma chave Fernet válida"""
    return Fernet.generate_key()

def validate_fernet_key(key: str) -> bool:
    """Valida se a chave Fernet está no formato correto"""
    try:
        # Verifica se a chave tem o tamanho correto (44 caracteres para base64)
        if len(key) != 44:
            return False
        
        # Tenta decodificar a chave
        decoded_key = base64.urlsafe_b64decode(key + '=' * (4 - len(key) % 4))
        
        # Verifica se tem 32 bytes
        if len(decoded_key) != 32:
            return False
            
        return True
    except Exception:
        return False

# Obter a chave de criptografia do ambiente
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

# Se não há chave ou se a chave não é válida, gera uma nova
if ENCRYPTION_KEY is None or not validate_fernet_key(ENCRYPTION_KEY):
    print("⚠️  ENCRYPTION_KEY não configurada ou inválida. Gerando nova chave...")
    ENCRYPTION_KEY = generate_fernet_key().decode()
    print(f"🔑 Nova chave gerada: {ENCRYPTION_KEY}")
    print("💡 Adicione esta chave ao seu arquivo .env como ENCRYPTION_KEY=")

try:
    fernet = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    print(f"❌ Erro ao inicializar Fernet: {e}")
    print("🔑 Gerando nova chave Fernet...")
    ENCRYPTION_KEY = generate_fernet_key().decode()
    fernet = Fernet(ENCRYPTION_KEY.encode())
    print(f"✅ Nova chave gerada e aplicada: {ENCRYPTION_KEY}")

def encrypt_session_id(session_id: str) -> bytes:
    """Criptografa o session_id."""
    return fernet.encrypt(session_id.encode())

def decrypt_session_id(encrypted_session_id: bytes) -> str:
    """Descriptografa o session_id."""
    return fernet.decrypt(encrypted_session_id).decode()

# Cria engine async
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True para debug SQL
    pool_pre_ping=True,
    pool_recycle=300,
    # Força o uso do driver asyncpg
    future=True,
    # Especifica explicitamente o driver
    connect_args={
        "server_settings": {
            "application_name": "instagram_api"
        }
    }
)

# Cria sessão async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

# Dependency para injeção de sessão
async def get_db():
    """Dependency para obter sessão do banco de dados"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Modelo InstagramAccount
class InstagramAccount(Base):
    __tablename__ = 'instagram_accounts'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    encrypted_session_id = Column(LargeBinary, nullable=False)
    last_synced = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<InstagramAccount {self.username}>'

    @property
    def session_id(self):
        return decrypt_session_id(self.encrypted_session_id)

    @session_id.setter
    def session_id(self, value):
        self.encrypted_session_id = encrypt_session_id(value) 