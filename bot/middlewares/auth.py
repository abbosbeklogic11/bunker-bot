"""
Authentication and User Registration Middleware for BUNKER bot.
Automatically creates/updates user records in PostgreSQL on every interaction.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser
from database.repositories import UserRepository


class AuthMiddleware(BaseMiddleware):
    def __init__(self, user_repo: UserRepository):
        super().__init__()
        self.user_repo = user_repo

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        tg_user: TelegramUser = data.get("event_from_user")
        if not tg_user or tg_user.is_bot:
            return await handler(event, data)

        # Upsert user record
        user = await self.user_repo.upsert(
            user_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name or "Foydalanuvchi"
        )

        if user.is_banned:
            # Silently ignore banned users
            return None

        data["user"] = user
        return await handler(event, data)
