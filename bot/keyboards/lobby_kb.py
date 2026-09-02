"""
Lobby keyboards for BUNKER game.
Provides direct Start/Join Telegram URL deep link for instantaneous joining.
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_lobby_keyboard(
    game_id: int,
    player_count: int,
    max_players: int = 20,
    is_creator: bool = False,
    bot_username: str = ""
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Direct deep-link URL button: opens bot in private with auto-join
    if bot_username:
        builder.button(text="🎮 O'yinga qo'shilish", url=f"https://t.me/{bot_username}?start=join_{game_id}")
    else:
        builder.button(text="🎮 O'yinga qo'shilish", callback_data=f"lobby_join:{game_id}")

    builder.button(text=f"👥 O'yinchilar ({player_count}/{max_players})", callback_data=f"lobby_players:{game_id}")
    builder.button(text="📖 Qoidalar", callback_data=f"lobby_rules:{game_id}")
    
    # Creator or Admin actions
    if is_creator or player_count >= 5:
        builder.button(text="🚀 O'yinni boshlash", callback_data=f"lobby_start:{game_id}")
    
    builder.button(text="❌ Bekor qilish", callback_data=f"lobby_cancel:{game_id}")

    builder.adjust(1, 2, 1, 1)
    return builder.as_markup()
