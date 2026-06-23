import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base
from urllib.parse import urlparse, urlunparse

DATABASE_URL = os.getenv("DATABASE_URL")

def get_clean_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not url.startswith("postgresql+asyncpg://"):
        url = "postgresql+asyncpg://" + url.split("://")[-1]
    parsed = urlparse(url)
    clean_url = urlunparse(parsed._replace(query=""))
    return clean_url

CLEAN_DB_URL = get_clean_url(DATABASE_URL)

engine = create_async_engine(
    CLEAN_DB_URL,
    echo=False,
    # asyncpg keshini o'chirib qo'yamiz, shunda jadval o'zgarsa xato bermaydi
    connect_args={
        "ssl": True,
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
