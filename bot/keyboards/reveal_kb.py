"""
Attribute selection keyboards for BUNKER game.
Allows each player to choose which specific attribute they want to reveal in the current round.
"""
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

ATTR_NAMES = {
    "profession": "👨‍💼 Kasb",
    "age": "🎂 Yosh",
    "health": "❤️ Sog'liq",
    "hobby": "🎯 Hobbi",
    "character": "🧠 Xarakter",
    "knowledge": "🎓 Bilim",
    "physical": "🏋️ Jismoniy",
    "inventory": "🎒 Buyum/Inventar",
    "genetics": "🧬 Genetika",
    "special": "🔬 Maxsus xususiyat"
}


def get_reveal_attribute_keyboard(game_id: int, unrevealed_attrs: List[str] = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keys = unrevealed_attrs if unrevealed_attrs is not None else list(ATTR_NAMES.keys())
    for attr in keys:
        name = ATTR_NAMES.get(attr, attr.title())
        builder.button(text=name, callback_data=f"reveal_attr:{game_id}:{attr}")

    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()
