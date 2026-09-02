"""
game/engine_events.py
Simple EventBus for decoupled communication between game engine and Telegram layer.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


class GameEventType(Enum):
    """All possible game event types emitted by the engine."""

    PLAYER_JOINED = "PlayerJoined"
    GAME_STARTED = "GameStarted"
    CARDS_DISTRIBUTED = "CardsDistributed"
    ATTRIBUTE_REVEALED = "AttributeRevealed"
    PLAYER_ATTRIBUTE_REVEALED = "PlayerAttributeRevealed"
    ABILITY_USED = "AbilityUsed"
    CARD_USED = "CardUsed"
    VOTE_SUBMITTED = "VoteSubmitted"
    ALL_VOTED = "AllVoted"
    PLAYER_ELIMINATED = "PlayerEliminated"
    EVENT_TRIGGERED = "EventTriggered"
    TIMER_EXPIRED = "TimerExpired"
    WINNER_DETERMINED = "WinnerDetermined"
    REWARD_GRANTED = "RewardGranted"
    GAME_FINISHED = "GameFinished"
    PHASE_CHANGED = "PhaseChanged"
    DUEL_STARTED = "DuelStarted"
    LOBBY_UPDATED = "LobbyUpdated"
    GAME_CANCELLED = "GameCancelled"


@dataclass
class GameEvent:
    """An event emitted by the GameEngine."""

    type: GameEventType
    game_id: int
    data: dict[str, Any] = field(default_factory=dict)


EventHandler = Callable[[GameEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Pub/sub message bus for game events."""

    def __init__(self) -> None:
        self._subscribers: dict[GameEventType, list[EventHandler]] = {}

    def subscribe(self, event_type: GameEventType, handler: EventHandler) -> None:
        """Register a coroutine handler for a specific event type."""
        self._subscribers.setdefault(event_type, []).append(handler)

    async def emit(self, event: GameEvent) -> None:
        """Deliver *event* to all subscribed handlers concurrently."""
        handlers = self._subscribers.get(event.type, [])
        if not handlers:
            return

        tasks = [asyncio.create_task(self._safe_call(h, event)) for h in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    async def _safe_call(handler: EventHandler, event: GameEvent) -> None:
        try:
            await handler(event)
        except Exception as exc:
            logger.exception("Unhandled error in event handler %s: %s", handler, exc)
