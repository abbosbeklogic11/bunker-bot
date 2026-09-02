"""
database/repositories/user_repo.py
User repository for DB interactions on users table and achievements.
"""
from __future__ import annotations
from typing import Any, Optional, List, Dict
import logging
from datetime import datetime, timezone
from models.user import UserModel

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1;", user_id)
        if row is None:
            return None
        return UserModel.from_row(row)

    async def upsert(
        self,
        user_id: int,
        username: Optional[str],
        first_name: str,
    ) -> UserModel:
        async with self._pool.acquire() as conn:
            # Check if user exists
            existing = await conn.fetchrow("SELECT * FROM users WHERE id = $1;", user_id)
            if existing:
                await conn.execute(
                    "UPDATE users SET username = $1, first_name = $2, updated_at = NOW() WHERE id = $3;",
                    username, first_name, user_id
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO users (id, username, first_name, is_bot_started, is_banned, is_admin, coins, diamonds, level, experience, reputation, games_played, games_won, games_lost, mvp_count, eliminations_count, survival_count, created_at, updated_at)
                    VALUES ($1, $2, $3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, NOW(), NOW());
                    """,
                    user_id, username, first_name
                )
            
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1;", user_id)
        return UserModel.from_row(row)

    async def set_bot_started(self, user_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_bot_started = 1, updated_at = NOW() WHERE id = $1;",
                user_id
            )

    async def is_bot_started(self, user_id: int) -> bool:
        async with self._pool.acquire() as conn:
            val = await conn.fetchval(
                "SELECT is_bot_started FROM users WHERE id = $1;", user_id
            )
        return bool(val)

    async def update_stats(self, user_id: int, **kwargs: Any) -> None:
        allowed = {
            "coins", "diamonds", "level", "experience", "reputation",
            "games_played", "games_won", "games_lost", "mvp_count",
            "eliminations_count", "survival_count",
        }
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        
        async with self._pool.acquire() as conn:
            for k, v in updates.items():
                await conn.execute(
                    f"UPDATE users SET {k} = {k} + $1, updated_at = NOW() WHERE id = $2;",
                    v, user_id
                )

    async def ban(self, user_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_banned = 1, updated_at = NOW() WHERE id = $1;",
                user_id
            )

    async def unban(self, user_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_banned = 0, updated_at = NOW() WHERE id = $1;",
                user_id
            )

    async def add_coins(self, user_id: int, amount: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET coins = coins + $1, updated_at = NOW() WHERE id = $2;",
                amount, user_id
            )

    async def add_diamonds(self, user_id: int, amount: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET diamonds = diamonds + $1, updated_at = NOW() WHERE id = $2;",
                amount, user_id
            )
