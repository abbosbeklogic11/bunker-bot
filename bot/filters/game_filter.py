"""
Chat type filters for BUNKER bot.
"""
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class IsGroupChat(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        chat = event.chat if isinstance(event, Message) else (event.message.chat if event.message else None)
        if not chat:
            return False
        return chat.type in ("group", "supergroup")


class IsPrivateChat(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        chat = event.chat if isinstance(event, Message) else (event.message.chat if event.message else None)
        if not chat:
            return False
        return chat.type == "private"
