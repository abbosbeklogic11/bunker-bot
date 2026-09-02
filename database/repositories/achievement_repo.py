from typing import Optional, List, Dict, Any
import asyncpg
from models.user import AchievementModel, UserAchievementModel, RewardModel


class AchievementRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_all_achievements(self) -> List[AchievementModel]:
        query = "SELECT * FROM achievements ORDER BY id ASC;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [AchievementModel.from_row(r) for r in rows]

    async def get_achievement_by_code(self, code: str) -> Optional[AchievementModel]:
        query = "SELECT * FROM achievements WHERE code = $1;"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, code)
            return AchievementModel.from_row(row) if row else None

    async def grant_achievement(self, user_id: int, achievement_id: int) -> bool:
        query = """
            INSERT INTO user_achievements (user_id, achievement_id, earned_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (user_id, achievement_id) DO NOTHING
            RETURNING achievement_id;
        """
        async with self.pool.acquire() as conn:
            val = await conn.fetchval(query, user_id, achievement_id)
            return val is not None

    async def get_user_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT a.code, a.name, a.description, a.icon, a.reward_coins, a.reward_diamonds, ua.earned_at
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
            WHERE ua.user_id = $1
            ORDER BY ua.earned_at DESC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return [dict(r) for r in rows]

    async def grant_reward(
        self,
        game_id: int,
        user_id: int,
        place: Optional[int] = None,
        coins: int = 0,
        diamonds: int = 0,
        bonus_type: Optional[str] = None
    ) -> RewardModel:
        query = """
            INSERT INTO rewards (game_id, user_id, place, coins_reward, diamonds_reward, bonus_type, granted_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, game_id, user_id, place, coins, diamonds, bonus_type)
            return RewardModel.from_row(row)
