"""
database/repositories/channel_repo.py
Repository for managing mandatory subscription channels and system settings.
"""
from typing import Any, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ChannelRepository:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def add_channel(self, channel_id: str, title: str, invite_link: str) -> bool:
        """Adds or updates a required channel."""
        query = """
            INSERT OR REPLACE INTO required_channels (channel_id, title, invite_link, is_active)
            VALUES ($1, $2, $3, 1);
        """
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(query, str(channel_id), title, invite_link)
                return True
        except Exception as e:
            logger.error(f"Error adding channel {channel_id}: {e}")
            return False

    async def remove_channel(self, channel_id: str) -> bool:
        """Deletes a required channel by channel_id or id."""
        query = "DELETE FROM required_channels WHERE channel_id = $1 OR id = $2;"
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(query, str(channel_id), str(channel_id))
                return True
        except Exception as e:
            logger.error(f"Error removing channel {channel_id}: {e}")
            return False

    async def get_all_channels(self) -> List[Dict[str, Any]]:
        """Returns all registered channels."""
        query = "SELECT * FROM required_channels ORDER BY id ASC;"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def get_active_channels(self) -> List[Dict[str, Any]]:
        """Returns all currently active mandatory channels."""
        query = "SELECT * FROM required_channels WHERE is_active = 1 ORDER BY id ASC;"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]

    async def toggle_channel_status(self, channel_id: str) -> bool:
        """Toggles active state of a channel."""
        query = """
            UPDATE required_channels 
            SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
            WHERE channel_id = $1 OR id = $2;
        """
        async with self._pool.acquire() as conn:
            await conn.execute(query, str(channel_id), str(channel_id))
            return True

    async def is_mandatory_sub_enabled(self) -> bool:
        """Checks if global mandatory subscription is active."""
        query = "SELECT value FROM system_settings WHERE key = 'mandatory_subscription_enabled';"
        async with self._pool.acquire() as conn:
            val = await conn.fetchval(query)
            return val in ("1", "true", "True", "TRUE", 1, True) if val is not None else True

    async def set_mandatory_sub_enabled(self, enabled: bool) -> None:
        """Enables or disables global mandatory subscription."""
        val_str = "1" if enabled else "0"
        query = "INSERT OR REPLACE INTO system_settings (key, value) VALUES ('mandatory_subscription_enabled', $1);"
        async with self._pool.acquire() as conn:
            await conn.execute(query, val_str)
