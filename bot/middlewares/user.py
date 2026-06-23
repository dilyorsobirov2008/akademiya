from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as tgUser
from database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
        
        # Check DB for user
        stmt = select(User).where(User.id == tg_user.id)
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()

        # Attach to data so handlers can use it
        data["db_user"] = db_user
        
        return await handler(event, data)
