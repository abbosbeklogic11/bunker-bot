"""
Game dashboard keyboards for BUNKER game.
Dynamically displays buttons for revealed attributes and phase-appropriate actions.
"""
from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_game_dashboard_keyboard(game_id: int, revealed_types: List[str], phase: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # 1. Players list button
    builder.button(text="👥 O'yinchilar", callback_data=f"game_view_players:{game_id}")

    # 2. Revealed attributes buttons
    attr_map = {
        "profession": ("👨‍💼 Kasblar", "attr_profession"),
        "age": ("🎂 Yosh", "attr_age"),
        "health": ("❤️ Sog'liq", "attr_health"),
        "character": ("🧠 Xarakter", "attr_character"),
        "hobby": ("🎯 Hobbi", "attr_hobby"),
        "knowledge": ("🎓 Bilim", "attr_knowledge"),
        "genetics": ("🧬 Genetika", "attr_genetics"),
        "physical": ("🏋️ Jismoniy", "attr_physical"),
        "inventory": ("🎒 Inventar", "attr_inventory"),
        "special": ("🔬 Maxsus", "attr_special")
    }

    for attr_type in revealed_types:
        if attr_type in attr_map:
            label, action = attr_map[attr_type]
            builder.button(text=label, callback_data=f"game_attr:{game_id}:{attr_type}")

    # 3. Phase action buttons
    if phase == "VOTING":
        builder.button(text="🗳 OVOZ BERISH", callback_data=f"game_open_voting:{game_id}")
    elif phase == "DUEL":
        builder.button(text="⚔️ DUEL OVOZI", callback_data=f"game_open_voting:{game_id}")

    # 4. Private chat action pointers & Stop button
    builder.button(text="⚡ Qobiliyatlar", callback_data=f"game_private_abilities:{game_id}")
    builder.button(text="🃏 Kartalarim", callback_data=f"game_private_cards:{game_id}")
    builder.button(text="📖 Qoidalar", callback_data=f"game_rules:{game_id}")
    builder.button(text="🛑 O'yinni to'xtatish", callback_data=f"game_stop:{game_id}")

    builder.adjust(1, 2, 2, 2, 2, 1)
    return builder.as_markup()


def get_back_to_game_keyboard(game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Dashboardga qaytish", callback_data=f"game_back:{game_id}")
    return builder.as_markup()
