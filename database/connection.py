from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("⚠️ CRITICAL: DATABASE_URL environment variable is missing!")
    DATABASE_URL = "postgresql+asyncpg://dummy:dummy@localhost/dummy"

# Fix: Render gives postgres:// but asyncpg needs postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remove channel_binding parameter (not supported by asyncpg)
if "channel_binding=" in DATABASE_URL:
    import re
    DATABASE_URL = re.sub(r'[&?]channel_binding=[^&]*', '', DATABASE_URL)

# SSL configuration for Neon/cloud DBs
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Remove sslmode from URL (handled by connect_args)
if "sslmode=" in DATABASE_URL:
    import re
    DATABASE_URL = re.sub(r'[&?]sslmode=[^&]*', '', DATABASE_URL)
    # Clean up trailing ? if present
    DATABASE_URL = DATABASE_URL.rstrip('?').rstrip('&')

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": ssl_context},
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    from database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
