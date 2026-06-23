from typing import Any, Awaitable, Callable, Dict
import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as tgUser
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: tgUser = data.get("event_from_user")
        if not tg_user:
            return await handler(event, data)

        session: AsyncSession = data.get("session")
        if not session:
             return await handler(event, data)

        try:
            # Check DB for user
            stmt = select(User).where(User.id == tg_user.id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            
            # Attach to data
            data["db_user"] = db_user
            logger.info(f"👤 User check: {tg_user.id} -> {'Found' if db_user else 'Not found'}")
        except Exception as e:
            logger.error(f"❌ UserMiddleware error: {e}")
            data["db_user"] = None
        
        return await handler(event, data)
