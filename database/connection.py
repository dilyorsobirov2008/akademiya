from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Instead of crashing at module import, we log and handle it
    print("CRITICAL: DATABASE_URL environment variable is missing!")
    # We can use a dummy URL for the engine to avoid module-level crash if its being imported for other purposes
    # but the real fix is setting the environment variable.
    DATABASE_URL = "postgresql+asyncpg://dummy:dummy@localhost/dummy" 

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    from database.models import Base
    async with engine.begin() as conn:
        # For development, you might want to drop all or use migrations
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
