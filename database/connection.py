import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base
from urllib.parse import urlparse, urlunparse

DATABASE_URL = os.getenv("DATABASE_URL")

def get_clean_url(url: str) -> str:
    if not url:
        return url
    
    # 1. Protokolni to'g'irlash
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not url.startswith("postgresql+asyncpg://"):
        url = "postgresql+asyncpg://" + url.split("://")[-1]

    # 2. Xalaqit beruvchi query parametrlarni o'chirish (sslmode, channel_binding)
    parsed = urlparse(url)
    clean_url = urlunparse(parsed._replace(query=""))
    return clean_url

CLEAN_DB_URL = get_clean_url(DATABASE_URL)

engine = create_async_engine(
    CLEAN_DB_URL,
    echo=False,
    connect_args={
        "ssl": True # Neon uchun SSL majburiy
    }
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
