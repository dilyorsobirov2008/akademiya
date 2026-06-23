import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base
import ssl

DATABASE_URL = os.getenv("DATABASE_URL")

# Neon/PostgreSQL uchun SSL sozlamalarini to'g'rilash
if DATABASE_URL and "sslmode=require" in DATABASE_URL:
    # asyncpg uchun ba'zi parametrlarni tozalash (agar ular xalaqit bersa)
    DATABASE_URL = DATABASE_URL.replace("channel_binding=require", "")
    # Agar URL postgresql:// bilan boshlansa, uni postgresql+asyncpg:// ga o'zgartirish
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={
        "ssl": True
    } if "sslmode=require" in DATABASE_URL else {}
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        # Jadvallarni yaratish
        await conn.run_sync(Base.metadata.create_all)
