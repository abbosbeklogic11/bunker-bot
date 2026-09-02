"""
Game-specific configuration constants.
All values can be overridden via environment variables (prefixed GAME_).
"""
from __future__ import annotations
from typing import Dict, Any, List

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class GameConfig(BaseSettings):
        """Tunable game-play constants with Pydantic settings."""

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            env_prefix="GAME_",
            case_sensitive=False,
            extra="ignore",
        )

        MAX_PLAYERS: int = 20
        MIN_PLAYERS: int = 5
        WINNERS_COUNT: int = 4

        LOBBY_TIMEOUT: int = 1800        # seconds (30 min)
        LOBBY_TIMER_WARN: int = 300      # warn 5 min before close

        REVEAL_TIME: int = 90            # 90 seconds (1.5 minutes) to choose & reveal attribute
        DISCUSSION_TIME: int = 120       # 2 minutes of discussion
        ABILITY_TIME: int = 30           # 30 seconds for abilities
        VOTING_TIME: int = 60            # 60 seconds of voting
        DUEL_TIME: int = 60
        EVENT_TIME: int = 45

        VOTE_CHANGE_ALLOWED: bool = False
        AUTO_START_ON_FULL: bool = True

        MAX_CARDS_PER_PLAYER: int = 3
        MAX_ABILITIES_PER_PLAYER: int = 2

        REWARD_PLACES: dict[int, dict[str, int]] = {
            1: {"coins": 500, "diamonds": 100},
            2: {"coins": 350, "diamonds": 70},
            3: {"coins": 250, "diamonds": 50},
            4: {"coins": 200, "diamonds": 40},
        }

        BONUS_REWARDS: dict[str, dict[str, int]] = {
            "mvp": {"coins": 150, "diamonds": 30},
            "longest_survivor": {"coins": 100, "diamonds": 20},
            "best_strategist": {"coins": 100, "diamonds": 20},
            "best_diplomat": {"coins": 100, "diamonds": 20},
            "most_protections": {"coins": 100, "diamonds": 20},
        }

except ImportError:
    from dataclasses import dataclass, field

    @dataclass
    class GameConfig:
        MAX_PLAYERS: int = 20
        MIN_PLAYERS: int = 5
        WINNERS_COUNT: int = 4

        LOBBY_TIMEOUT: int = 1800
        LOBBY_TIMER_WARN: int = 300

        REVEAL_TIME: int = 90
        DISCUSSION_TIME: int = 120
        ABILITY_TIME: int = 30
        VOTING_TIME: int = 60
        DUEL_TIME: int = 60
        EVENT_TIME: int = 45

        VOTE_CHANGE_ALLOWED: bool = False
        AUTO_START_ON_FULL: bool = True

        MAX_CARDS_PER_PLAYER: int = 3
        MAX_ABILITIES_PER_PLAYER: int = 2

        REWARD_PLACES: dict = field(default_factory=lambda: {
            1: {"coins": 500, "diamonds": 100},
            2: {"coins": 350, "diamonds": 70},
            3: {"coins": 250, "diamonds": 50},
            4: {"coins": 200, "diamonds": 40},
        })

        BONUS_REWARDS: dict = field(default_factory=lambda: {
            "mvp": {"coins": 150, "diamonds": 30},
            "longest_survivor": {"coins": 100, "diamonds": 20},
            "best_strategist": {"coins": 100, "diamonds": 20},
            "best_diplomat": {"coins": 100, "diamonds": 20},
            "most_protections": {"coins": 100, "diamonds": 20},
        })


default_game_config = GameConfig()
