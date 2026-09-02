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

    async def get_total_users_count(self) -> int:
        async with self._pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM users;") or 0

    async def get_today_users_count(self) -> int:
        async with self._pool.acquire() as conn:
            # Compatible with both SQLite and Postgres
            try:
                return await conn.fetchval("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now');") or 0
            except Exception:
                return await conn.fetchval("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE;") or 0

    async def set_admin(self, user_id: int, is_admin: bool = True) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_admin = $1, updated_at = NOW() WHERE id = $2;",
                1 if is_admin else 0, user_id
            )

    async def get_admin_count(self) -> int:
        async with self._pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_admin = 1;") or 0

    # ==================== REFERRAL SYSTEM ====================

    async def record_referral(
        self,
        referrer_id: int,
        referred_id: int,
        bonus_coins: int = 50,
        bonus_diamonds: int = 10,
        newcomer_bonus_coins: int = 30
    ) -> bool:
        """Records a new referral, rewarding the referrer and the newcomer."""
        if referrer_id == referred_id:
            return False

        async with self._pool.acquire() as conn:
            # Check if newcomer already has a recorded referrer
            existing = await conn.fetchval("SELECT id FROM referrals WHERE referred_id = $1;", referred_id)
            if existing:
                return False

            # Insert referral record
            await conn.execute(
                """
                INSERT INTO referrals (referrer_id, referred_id, bonus_coins, bonus_diamonds)
                VALUES ($1, $2, $3, $4);
                """,
                referrer_id, referred_id, bonus_coins, bonus_diamonds
            )

            # Reward referrer
            await conn.execute(
                "UPDATE users SET coins = coins + $1, diamonds = diamonds + $2, updated_at = NOW() WHERE id = $3;",
                bonus_coins, bonus_diamonds, referrer_id
            )

            # Reward newcomer
            await conn.execute(
                "UPDATE users SET coins = coins + $1, updated_at = NOW() WHERE id = $2;",
                newcomer_bonus_coins, referred_id
            )
            return True

    async def get_referral_stats(self, user_id: int) -> Dict[str, Any]:
        """Returns referral statistics for a user."""
        async with self._pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM referrals WHERE referrer_id = $1;", user_id) or 0
            earned_coins = await conn.fetchval("SELECT COALESCE(SUM(bonus_coins), 0) FROM referrals WHERE referrer_id = $1;", user_id) or 0
            earned_diamonds = await conn.fetchval("SELECT COALESCE(SUM(bonus_diamonds), 0) FROM referrals WHERE referrer_id = $1;", user_id) or 0
            return {
                "total_referrals": count,
                "earned_coins": earned_coins,
                "earned_diamonds": earned_diamonds
            }

    # ==================== SHOP / INVENTORY SYSTEM ====================

    async def buy_inventory_item(self, user_id: int, item_code: str, item_name: str, cost: int) -> Dict[str, Any]:
        """Buys an item from the shop, deducting coins if user has enough balance."""
        user = await self.get_by_id(user_id)
        if not user:
            return {"success": False, "error": "USER_NOT_FOUND"}

        if user.coins < cost:
            return {"success": False, "error": "INSUFFICIENT_FUNDS", "user_coins": user.coins, "cost": cost}

        async with self._pool.acquire() as conn:
            # Deduct coins
            await conn.execute(
                "UPDATE users SET coins = coins - $1, updated_at = NOW() WHERE id = $2;",
                cost, user_id
            )
            # Add to inventory
            await conn.execute(
                """
                INSERT INTO user_inventory (user_id, item_code, item_name, quantity)
                VALUES ($1, $2, $3, 1);
                """,
                user_id, item_code, item_name
            )

        new_user = await self.get_by_id(user_id)
        return {"success": True, "new_balance": new_user.coins if new_user else 0}

    async def get_user_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Returns all purchased items currently in user's inventory."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM user_inventory WHERE user_id = $1 AND quantity > 0 ORDER BY id ASC;",
                user_id
            )
            return [dict(r) for r in rows]

    async def consume_inventory_item(self, user_id: int, item_code: str) -> bool:
        """Consumes 1 quantity of an inventory item during game usage."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, quantity FROM user_inventory WHERE user_id = $1 AND item_code = $2 AND quantity > 0 LIMIT 1;",
                user_id, item_code
            )
            if not row:
                return False
            
            inv_id = row["id"]
            qty = row["quantity"]
            if qty > 1:
                await conn.execute("UPDATE user_inventory SET quantity = quantity - 1 WHERE id = $1;", inv_id)
            else:
                await conn.execute("DELETE FROM user_inventory WHERE id = $1;", inv_id)
            return True
