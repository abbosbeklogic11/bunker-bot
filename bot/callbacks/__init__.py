from .lobby_cb import router as lobby_cb_router
from .game_cb import router as game_cb_router
from .voting_cb import router as voting_cb_router
from .ability_cb import router as ability_cb_router
from .card_cb import router as card_cb_router

__all__ = [
    "lobby_cb_router",
    "game_cb_router",
    "voting_cb_router",
    "ability_cb_router",
    "card_cb_router",
]
