"""
Pydantic models for game domain entities.
These are pure data models — not ORM, not DB-specific.
"""
from __future__ import annotations
import enum
import json
from datetime import datetime
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, ConfigDict


# =============================================================
# Enumerations
# =============================================================

class GameState(str, enum.Enum):
    """Finite states of a single game session."""
    LOBBY            = "LOBBY"
    STARTING         = "STARTING"
    DEAL_CARDS       = "DEAL_CARDS"
    REVEAL_ATTRIBUTE = "REVEAL_ATTRIBUTE"
    DISCUSSION       = "DISCUSSION"
    ABILITY_PHASE    = "ABILITY_PHASE"
    VOTING           = "VOTING"
    DUEL             = "DUEL"
    ELIMINATION      = "ELIMINATION"
    EVENT            = "EVENT"
    CHECK_WIN        = "CHECK_WIN"
    FINAL            = "FINAL"
    REWARDS          = "REWARDS"
    FINISHED         = "FINISHED"


class PlayerStatus(str, enum.Enum):
    """Possible statuses for a player in a game."""
    ACTIVE       = "ACTIVE"
    ELIMINATED   = "ELIMINATED"
    LEFT         = "LEFT"
    DISCONNECTED = "DISCONNECTED"
    WINNER       = "WINNER"
    LOSER        = "LOSER"
    PROTECTED    = "PROTECTED"


class Rarity(str, enum.Enum):
    """Card rarity tiers."""
    COMMON    = "COMMON"
    UNCOMMON  = "UNCOMMON"
    RARE      = "RARE"
    EPIC      = "EPIC"
    LEGENDARY = "LEGENDARY"


class AttributeType(str, enum.Enum):
    """Player character attribute categories."""
    profession = "profession"
    age        = "age"
    health     = "health"
    character  = "character"
    hobby      = "hobby"
    knowledge  = "knowledge"
    genetics   = "genetics"
    physical   = "physical"
    inventory  = "inventory"
    special    = "special"


# =============================================================
# Helper function for parsing DB rows
# =============================================================

def _clean_row(row: Any) -> Dict[str, Any]:
    if row is None:
        return {}
    d = dict(row)
    for k, v in list(d.items()):
        if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
            try:
                d[k] = json.loads(v)
            except Exception:
                pass
    return d


# =============================================================
# Game Models
# =============================================================

class GameModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                      int
    group_chat_id:           int
    dashboard_message_id:    Optional[int] = None
    state:                   GameState = GameState.LOBBY
    current_round:           int = 0
    current_attribute_index: int = 0
    apocalypse_type:         Optional[str] = None
    bunker_capacity:         int = 4
    bunker_food_days:        Optional[int] = None
    bunker_water_days:       Optional[int] = None
    bunker_power_days:       Optional[int] = None
    bunker_has_farm:         bool = False
    bunker_has_medical:      bool = False
    bunker_has_workshop:     bool = False
    bunker_has_radio:        bool = False
    phase_started_at:        Optional[Any] = None
    phase_ends_at:           Optional[Any] = None
    config:                  Dict[str, Any] = {}
    created_by:              Optional[int] = None
    created_at:              Optional[Any] = None
    finished_at:             Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "GameModel":
        return cls(**_clean_row(row))

    @property
    def is_active(self) -> bool:
        return self.state != GameState.FINISHED

    @property
    def is_in_lobby(self) -> bool:
        return self.state == GameState.LOBBY


class GamePlayerModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                    int = 0
    game_id:               int = 0
    user_id:               int = 0
    status:                PlayerStatus = PlayerStatus.ACTIVE
    survival_score:        int = 0
    is_protected:          bool = False
    protected_until_round: Optional[int] = None
    join_order:            Optional[int] = None
    elimination_round:     Optional[int] = None
    elimination_votes:     int = 0
    votes_received_total:  int = 0
    votes_given_total:     int = 0
    abilities_used:        int = 0
    cards_used:            int = 0
    joined_at:             Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "GamePlayerModel":
        return cls(**_clean_row(row))


class PlayerAttributeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                 int
    game_id:            int
    user_id:            int
    attribute_type:     str
    attribute_value:    str
    attribute_metadata: Dict[str, Any] = {}
    is_revealed:        bool = False
    is_fake:            bool = False
    revealed_at:        Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "PlayerAttributeModel":
        return cls(**_clean_row(row))


class VoteModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           int
    game_id:      int
    round_number: int
    voter_id:     int
    target_id:    int
    vote_weight:  int = 1
    is_valid:     bool = True
    created_at:   Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "VoteModel":
        return cls(**_clean_row(row))


class CardModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    name:        str
    description: str = ""
    rarity:      Rarity = Rarity.COMMON
    power:       int = 1
    card_type:   str
    effect_data: Dict[str, Any] = {}
    is_active:   bool = True

    @classmethod
    def from_row(cls, row: Any) -> "CardModel":
        return cls(**_clean_row(row))


class AbilityModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                int
    name:              str
    description:       str = ""
    ability_type:      str
    trigger_condition: str = "manual"
    power:             int = 1
    uses_per_game:     int = 1
    effect_data:       Dict[str, Any] = {}
    is_active:         bool = True

    @classmethod
    def from_row(cls, row: Any) -> "AbilityModel":
        return cls(**_clean_row(row))


class GameEventModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           int
    game_id:      int
    round_number: int = 0
    event_type:   str
    event_data:   Dict[str, Any] = {}
    triggered_at: Optional[Any] = None
    resolved:     bool = False
    resolved_by:  Optional[int] = None

    @classmethod
    def from_row(cls, row: Any) -> "GameEventModel":
        return cls(**_clean_row(row))


class ActionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:           int
    game_id:      int
    round_number: Optional[int] = 0
    actor_id:     Optional[int] = None
    action_type:  str
    action_data:  Dict[str, Any] = {}
    created_at:   Optional[Any] = None

    @classmethod
    def from_row(cls, row: Any) -> "ActionModel":
        return cls(**_clean_row(row))
