"""
services/subscription_service.py
Service for checking mandatory channel subscriptions for users.
"""
from typing import Tuple, List, Dict, Any, Optional
import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.repositories import ChannelRepository

logger = logging.getLogger(__name__)


class SubscriptionService:
    @staticmethod
    async def check_user_subscription(
        bot: Bot,
        user_id: int,
        channel_repo: ChannelRepository
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Checks if user is subscribed to all active mandatory channels.
        Returns (is_all_subscribed, unjoined_channels_list).
        """
        is_enabled = await channel_repo.is_mandatory_sub_enabled()
        if not is_enabled:
            return True, []

        channels = await channel_repo.get_active_channels()
        if not channels:
            return True, []

        unjoined = []
        for ch in channels:
            ch_id = ch["channel_id"]
            try:
                member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
                if member.status not in ("creator", "administrator", "member", "restricted"):
                    unjoined.append(ch)
            except Exception as e:
                logger.warning(f"Could not check membership for channel {ch_id} and user {user_id}: {e}")
                # If bot cannot check (e.g. not admin in channel), consider unjoined
                unjoined.append(ch)

        return len(unjoined) == 0, unjoined

    @staticmethod
    def get_subscription_keyboard(unjoined_channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Builds inline keyboard with channel links and verification button."""
        builder = InlineKeyboardBuilder()
        for idx, ch in enumerate(unjoined_channels, 1):
            title = ch.get("title", f"Kanal #{idx}")
            link = ch.get("invite_link", "https://t.me")
            builder.button(text=f"📢 {title}", url=link)

        builder.button(text="✅ A'zolikni tekshirish", callback_data="check_subscription_status")
        builder.adjust(1)
        return builder.as_markup()
