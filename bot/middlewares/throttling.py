"""
Throttling Middleware to prevent spam button clicking and race conditions.
"""
from typing import Callable, Dict, Any, Awaitable
import time
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit_sec: float = 0.5):
        super().__init__()
        self.rate_limit = rate_limit_sec
        self._user_last_action: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        uid = user.id
        now = time.time()
        last_time = self._user_last_action.get(uid, 0.0)

        if now - last_time < self.rate_limit:
            if isinstance(event, CallbackQuery):
                await event.answer("⚠️ Iltimos, biroz kuting...", show_alert=False)
            return None

        self._user_last_action[uid] = now
        return await handler(event, data)
