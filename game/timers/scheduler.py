"""
game/timers/scheduler.py
High-precision game phase watchdog that fires phase-timeout logic automatically.
Uses an internal asyncio timer loop (1-second tick) for instantaneous phase transitions.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Set

from game.timers.timer_engine import TimerEngine

if TYPE_CHECKING:
    from game.engine import GameEngine

logger = logging.getLogger(__name__)

_CHECK_INTERVAL_SECONDS = 1


class GameScheduler:
    def __init__(self, timer_engine: TimerEngine, game_engine: "GameEngine") -> None:
        self._timer_engine = timer_engine
        self._game_engine = game_engine
        self._in_flight: Set[int] = set()
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start the high-precision background timer loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("GameScheduler started (tick interval=%ss)", _CHECK_INTERVAL_SECONDS)

    async def stop(self) -> None:
        """Gracefully shut down the scheduler loop."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("GameScheduler stopped")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self._check_expired_phases()
            except Exception as e:
                logger.error(f"Error in scheduler tick: {e}")
            await asyncio.sleep(_CHECK_INTERVAL_SECONDS)

    async def _check_expired_phases(self) -> None:
        try:
            active_timers = await self._timer_engine.get_active_timers()
        except Exception as exc:
            logger.exception(f"Failed to fetch active timers: {exc}")
            return

        now = int(time.time())
        for timer in active_timers:
            game_id: int = timer.get("game_id", -1)
            phase: str = timer.get("phase", "")
            ends_at: int = timer.get("ends_at", 0)

            if game_id < 0 or not phase:
                continue

            if game_id in self._in_flight:
                continue

            if ends_at <= now:
                self._in_flight.add(game_id)
                try:
                    logger.info(f"Phase timeout detected: game_id={game_id} phase={phase}")
                    await self._timer_engine.cancel_timer(game_id)
                    await self._game_engine.handle_phase_timeout(game_id, phase)
                except Exception as exc:
                    logger.exception(f"Error handling phase timeout for game {game_id}: {exc}")
                finally:
                    self._in_flight.discard(game_id)
