"""
game/timers/timer_engine.py
Redis-backed timer engine with automatic in-memory fallback.
Works flawlessly even when Redis is not installed.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_TIMER_PREFIX = "timer:game:"


class TimerEngine:
    """
    Manages per-game phase timers stored in Redis with local in-memory fallback.
    """

    def __init__(self, redis_client: Optional[Any] = None) -> None:
        self._redis = redis_client
        self._memory_timers: Dict[str, Dict[str, Any]] = {}

    def _key(self, game_id: int) -> str:
        return f"{_TIMER_PREFIX}{game_id}"

    async def set_phase_timer(
        self,
        game_id: int,
        phase: str,
        duration_seconds: int,
    ) -> None:
        ends_at = int(time.time()) + duration_seconds
        payload = {
            "phase": phase,
            "ends_at": ends_at,
            "game_id": game_id,
        }

        if self._redis is not None:
            try:
                await self._redis.setex(self._key(game_id), duration_seconds + 3600, json.dumps(payload))
                return
            except Exception:
                pass

        # In-memory storage
        self._memory_timers[self._key(game_id)] = payload

    async def get_remaining_time(self, game_id: int) -> int:
        now = int(time.time())

        if self._redis is not None:
            try:
                raw = await self._redis.get(self._key(game_id))
                if raw is not None:
                    data = json.loads(raw)
                    return max(0, int(data["ends_at"]) - now)
            except Exception:
                pass

        data = self._memory_timers.get(self._key(game_id))
        if data:
            rem = int(data["ends_at"]) - now
            return max(0, rem)
        return 0

    async def cancel_timer(self, game_id: int) -> None:
        if self._redis is not None:
            try:
                await self._redis.delete(self._key(game_id))
            except Exception:
                pass
        self._memory_timers.pop(self._key(game_id), None)

    async def is_expired(self, game_id: int) -> bool:
        return (await self.get_remaining_time(game_id)) == 0

    async def get_phase_info(self, game_id: int) -> Optional[Dict[str, Any]]:
        now = int(time.time())

        if self._redis is not None:
            try:
                raw = await self._redis.get(self._key(game_id))
                if raw is not None:
                    data = json.loads(raw)
                    data["remaining_seconds"] = max(0, int(data["ends_at"]) - now)
                    return data
            except Exception:
                pass

        data = self._memory_timers.get(self._key(game_id))
        if data:
            rem = max(0, int(data["ends_at"]) - now)
            data["remaining_seconds"] = rem
            return data
        return None

    async def get_active_timers(self) -> List[Dict[str, Any]]:
        now = int(time.time())
        results = []

        if self._redis is not None:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor, match="timer:game:*", count=100)
                    for key in keys:
                        raw = await self._redis.get(key)
                        if raw:
                            d = json.loads(raw)
                            d["remaining_seconds"] = max(0, int(d["ends_at"]) - now)
                            results.append(d)
                    if cursor == 0:
                        break
                return results
            except Exception:
                pass

        for k, v in list(self._memory_timers.items()):
            rem = max(0, int(v["ends_at"]) - now)
            v["remaining_seconds"] = rem
            results.append(v)

        return results
