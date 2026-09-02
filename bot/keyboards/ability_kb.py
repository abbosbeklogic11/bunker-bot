"""
Ability and card management keyboards for Private chat in BUNKER game.
"""
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_player_abilities_keyboard(game_id: int, abilities: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for ab in abilities:
        ab_id = ab.get("ability_id")
        name = ab.get("name", "Qobiliyat")
        uses = ab.get("uses_remaining", 0)
        blocked = ab.get("is_blocked", False)

        if blocked:
            status_tag = "🔒 BLOKLANGAN"
        elif uses > 0:
            status_tag = f"✅ ({uses} ta)"
        else:
            status_tag = "⛔ ISHLATILGAN"

        builder.button(text=f"{name} — {status_tag}", callback_data=f"use_ab_select:{game_id}:{ab_id}")

    builder.adjust(1)
    return builder.as_markup()


def get_ability_target_keyboard(game_id: int, ability_id: int, alive_players: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for p in alive_players:
        uid = p["user_id"]
        name = p.get("name", f"O'yinchi #{uid}")
        builder.button(text=f"🎯 {name}", callback_data=f"use_ab_target:{game_id}:{ability_id}:{uid}")

    builder.button(text="⬅️ Bekor qilish", callback_data=f"mygame_abilities:{game_id}")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def get_player_cards_keyboard(game_id: int, cards: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for c in cards:
        pc_id = c.get("player_card_id")
        name = c.get("name", "Karta")
        rarity = c.get("rarity", "COMMON")
        is_used = c.get("is_used", False)

        rarity_icons = {
            "COMMON": "⚪", "UNCOMMON": "🟢", "RARE": "🔵", "EPIC": "🟣", "LEGENDARY": "🟡"
        }
        icon = rarity_icons.get(rarity, "🃏")
        status = "⛔ ISHLATILGAN" if is_used else f"{icon} {rarity}"

        builder.button(text=f"{name} [{status}]", callback_data=f"use_card_select:{game_id}:{pc_id}")

    builder.adjust(1)
    return builder.as_markup()


def get_card_target_keyboard(game_id: int, player_card_id: int, alive_players: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="👤 O'zimga ishlatish", callback_data=f"use_card_target:{game_id}:{player_card_id}:0")
    for p in alive_players:
        uid = p["user_id"]
        name = p.get("name", f"O'yinchi #{uid}")
        builder.button(text=f"🎯 {name}", callback_data=f"use_card_target:{game_id}:{player_card_id}:{uid}")

    builder.button(text="⬅️ Bekor qilish", callback_data=f"mygame_cards:{game_id}")
    builder.adjust(1, 2, 2, 1)
    return builder.as_markup()
