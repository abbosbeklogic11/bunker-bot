"""
Lobby keyboards for BUNKER game.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_lobby_keyboard(game_id: int, player_count: int, max_players: int = 20, is_creator: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Main Join button
    builder.button(text="➕ O'yinga qo'shilish", callback_data=f"lobby_join:{game_id}")
    builder.button(text=f"👥 O'yinchilar ({player_count}/{max_players})", callback_data=f"lobby_players:{game_id}")
    builder.button(text="📖 Qoidalar", callback_data=f"lobby_rules:{game_id}")
    
    # Creator or Admin actions
    if is_creator or player_count >= 5:
        builder.button(text="🚀 O'yinni boshlash", callback_data=f"lobby_start:{game_id}")
    
    builder.button(text="❌ Bekor qilish", callback_data=f"lobby_cancel:{game_id}")

    builder.adjust(1, 2, 1, 1)
    return builder.as_markup()
