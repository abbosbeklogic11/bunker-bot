"""
Voting keyboards for BUNKER game.
Shows live real-time vote count on candidate buttons without dashboard distraction.
"""
from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_voting_keyboard(
    game_id: int,
    alive_players: List[Dict[str, Any]],
    voter_id: int = 0,
    votes_tally: Optional[Dict[int, int]] = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    tally = votes_tally or {}

    for p in alive_players:
        uid = p["user_id"]
        name = p.get("name", f"O'yinchi #{uid}")
        
        # Don't show voter themselves if self-voting is not allowed
        if voter_id and uid == voter_id:
            continue
        
        vote_count = tally.get(uid, 0)
        if vote_count > 0:
            btn_text = f"🔴 {name} ({vote_count} ta ovoz)"
        else:
            btn_text = f"🔴 {name}"

        builder.button(text=btn_text, callback_data=f"vote:{game_id}:{uid}")

    builder.adjust(1)
    return builder.as_markup()


def get_duel_voting_keyboard(
    game_id: int,
    duel_candidates: List[Dict[str, Any]],
    voter_id: int = 0,
    votes_tally: Optional[Dict[int, int]] = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    tally = votes_tally or {}

    for p in duel_candidates:
        uid = p["user_id"]
        name = p.get("name", f"Nomzod #{uid}")
        
        vote_count = tally.get(uid, 0)
        if vote_count > 0:
            btn_text = f"⚔️ {name} ({vote_count} ta ovoz)"
        else:
            btn_text = f"⚔️ {name}"

        builder.button(text=btn_text, callback_data=f"vote:{game_id}:{uid}")

    builder.adjust(1)
    return builder.as_markup()
