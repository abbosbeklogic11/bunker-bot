from typing import Optional, List, Dict, Any
import asyncpg
import json
from models.game import GameEventModel


class EventRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_event(
        self,
        game_id: int,
        round_number: int,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> GameEventModel:
        query = """
            INSERT INTO game_events (game_id, round_number, event_type, event_data, triggered_at, resolved)
            VALUES ($1, $2, $3, $4, NOW(), FALSE)
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, game_id, round_number, event_type, json.dumps(event_data or {}))
            return GameEventModel.from_row(row)

    async def resolve_event(self, event_id: int, resolved_by: Optional[int] = None) -> None:
        query = "UPDATE game_events SET resolved = TRUE, resolved_by = $1 WHERE id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, resolved_by, event_id)

    async def get_unresolved_events(self, game_id: int) -> List[GameEventModel]:
        query = "SELECT * FROM game_events WHERE game_id = $1 AND resolved = FALSE ORDER BY id ASC;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id)
            return [GameEventModel.from_row(r) for r in rows]

    async def get_events_for_game(self, game_id: int) -> List[GameEventModel]:
        query = "SELECT * FROM game_events WHERE game_id = $1 ORDER BY round_number ASC, id ASC;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, game_id)
            return [GameEventModel.from_row(r) for r in rows]
