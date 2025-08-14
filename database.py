import os
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

# Obter a chave de criptografia do ambiente
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if ENCRYPTION_KEY is None:
    raise ValueError("ENCRYPTION_KEY environment variable not set. Please generate one and set it.")

fernet = Fernet(ENCRYPTION_KEY)

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