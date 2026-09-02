from typing import Optional, List, Dict, Any
import asyncpg
import json
from datetime import datetime, timezone
from models.game import GameModel, GameState, ActionModel


class GameRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_game(self, group_chat_id: int, created_by: int, config: Optional[Dict[str, Any]] = None) -> GameModel:
        query = """
            INSERT INTO games (group_chat_id, created_by, state, config, phase_started_at)
            VALUES ($1, $2, 'LOBBY', $3, NOW())
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, group_chat_id, created_by, json.dumps(config or {}))
            return GameModel.from_row(row)

    async def get_by_id(self, game_id: int) -> Optional[GameModel]:
        query = "SELECT * FROM games WHERE id = $1;"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, game_id)
            return GameModel.from_row(row) if row else None

    async def get_active_game_by_group(self, group_chat_id: int) -> Optional[GameModel]:
        query = """
            SELECT * FROM games 
            WHERE group_chat_id = $1 AND state NOT IN ('FINISHED')
            ORDER BY id DESC LIMIT 1;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, group_chat_id)
            return GameModel.from_row(row) if row else None

    async def get_active_games(self) -> List[GameModel]:
        query = "SELECT * FROM games WHERE state NOT IN ('FINISHED') ORDER BY id ASC;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [GameModel.from_row(r) for r in rows]

    async def update_state(self, game_id: int, state: GameState) -> None:
        state_str = state.value if isinstance(state, GameState) else str(state)
        query = "UPDATE games SET state = $1 WHERE id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, state_str, game_id)

    async def update_phase_times(self, game_id: int, started_at: datetime, ends_at: datetime) -> None:
        query = """
            UPDATE games 
            SET phase_started_at = $1, phase_ends_at = $2 
            WHERE id = $3;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, started_at, ends_at, game_id)

    async def update_dashboard_message_id(self, game_id: int, message_id: int) -> None:
        query = "UPDATE games SET dashboard_message_id = $1 WHERE id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, message_id, game_id)

    async def set_apocalypse(self, game_id: int, apocalypse_type: str) -> None:
        query = "UPDATE games SET apocalypse_type = $1 WHERE id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, apocalypse_type, game_id)

    async def set_bunker_config(
        self,
        game_id: int,
        capacity: int = 4,
        food_days: int = 180,
        water_days: int = 150,
        power_days: int = 90,
        has_farm: bool = False,
        has_medical: bool = False,
        has_workshop: bool = False,
        has_radio: bool = False
    ) -> None:
        query = """
            UPDATE games 
            SET bunker_capacity = $1, bunker_food_days = $2, bunker_water_days = $3, bunker_power_days = $4,
                bunker_has_farm = $5, bunker_has_medical = $6, bunker_has_workshop = $7, bunker_has_radio = $8
            WHERE id = $9;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                query, capacity, food_days, water_days, power_days,
                has_farm, has_medical, has_workshop, has_radio, game_id
            )

    async def increment_round(self, game_id: int) -> int:
        query = "UPDATE games SET current_round = current_round + 1 WHERE id = $1 RETURNING current_round;"
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, game_id)

    async def finish_game(self, game_id: int) -> None:
        query = "UPDATE games SET state = 'FINISHED', finished_at = NOW() WHERE id = $1;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, game_id)

    async def update_config(self, game_id: int, config: Dict[str, Any]) -> None:
        query = "UPDATE games SET config = $1 WHERE id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, json.dumps(config), game_id)

    async def log_action(
        self,
        game_id: int,
        round_number: Optional[int],
        actor_id: Optional[int],
        action_type: str,
        action_data: Optional[Dict[str, Any]] = None
    ) -> ActionModel:
        query = """
            INSERT INTO actions (game_id, round_number, actor_id, action_type, action_data)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                query, game_id, round_number, actor_id, action_type, json.dumps(action_data or {})
            )
            return ActionModel.from_row(row)

    async def get_game_log(self, game_id: int, limit: int = 50) -> List[ActionModel]:
        query = """
            SELECT * FROM actions 
            WHERE game_id = $1 
            ORDER BY id ASC LIMIT $2;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id, limit)
            return [ActionModel.from_row(r) for r in rows]

    async def get_total_games_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM games;") or 0

    async def get_active_games_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM games WHERE state != 'FINISHED';") or 0

    async def get_total_groups_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(DISTINCT group_chat_id) FROM games;") or 0
