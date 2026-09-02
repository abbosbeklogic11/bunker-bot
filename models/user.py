# Pydantic models for user domain entities.
from __future__ import annotations
from typing import Any, Optional, Dict
from pydantic import BaseModel, ConfigDict


def _clean_row(row: Any) -> Dict[str, Any]:
    if row is None:
        return {}
    return dict(row)


class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                 int
    username:           Optional[str] = None
    first_name:         str = ""
    is_bot_started:     bool = False
    is_banned:          bool = False
    is_admin:           bool = False
    coins:              int = 0
    diamonds:           int = 0
    level:              int = 1
    experience:         int = 0
    reputation:         int = 0
    games_played:       int = 0
    games_won:          int = 0
    games_lost:         int = 0
    mvp_count:          int = 0
    eliminations_count: int = 0
    survival_count:     int = 0
    created_at:         Optional[Any] = None
    updated_at:         Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "UserModel":
        return cls(**_clean_row(row))

    @property
    def display_name(self) -> str:
        if self.username:
            return f"@{self.username}"
        return self.first_name or f"User#{self.id}"

    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return round(self.games_won / self.games_played * 100, 1)


class AchievementModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:              int
    code:            str
    name:            str
    description:     str = ""
    icon:            str = ""
    reward_coins:    int = 0
    reward_diamonds: int = 0

    @classmethod
    def from_row(cls, row: Any) -> "AchievementModel":
        return cls(**_clean_row(row))


class UserAchievementModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id:        int
    achievement_id: int
    earned_at:      Optional[Any] = None
    achievement:    Optional[AchievementModel] = None

    @classmethod
    def from_row(cls, row: Any) -> "UserAchievementModel":
        return cls(**_clean_row(row))


class RewardModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:              int
    game_id:         int
    user_id:         int
    place:           Optional[int] = None
    coins_reward:    int = 0
    diamonds_reward: int = 0
    bonus_type:      Optional[str] = None
    granted_at:      Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "RewardModel":
        return cls(**_clean_row(row))
