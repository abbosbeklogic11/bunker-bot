"""
Admin filters for BUNKER bot.
"""
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from bot.config.settings import settings
from models.user import UserModel


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, user: UserModel) -> bool:
        if not user:
            return False
        return user.is_admin or user.id in settings.ADMIN_IDS
