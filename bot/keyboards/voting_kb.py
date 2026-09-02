"""
Voting keyboards for BUNKER game.
"""
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_voting_keyboard(game_id: int, alive_players: List[Dict[str, Any]], voter_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for p in alive_players:
        uid = p["user_id"]
        name = p.get("name", f"O'yinchi #{uid}")
        
        # Don't show voter themselves if self-voting is not allowed
        if uid == voter_id:
            continue
        
        builder.button(text=f"🔴 {name}", callback_data=f"vote:{game_id}:{uid}")

    builder.button(text="⬅️ Dashboardga qaytish", callback_data=f"game_back:{game_id}")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def get_duel_voting_keyboard(game_id: int, duel_candidates: List[Dict[str, Any]], voter_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for p in duel_candidates:
        uid = p["user_id"]
        name = p.get("name", f"Nomzod #{uid}")
        builder.button(text=f"⚔️ {name}", callback_data=f"vote:{game_id}:{uid}")

    builder.adjust(1)
    return builder.as_markup()
