"""
Admin management keyboards for BUNKER game.
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="🎮 Faol o'yinlar", callback_data="admin_active_games")
    builder.button(text="👥 Foydalanuvchilar", callback_data="admin_users")
    builder.button(text="⚙️ Game sozlamalari", callback_data="admin_settings")
    builder.button(text="📊 Global statistika", callback_data="admin_stats")

    builder.adjust(2, 2)
    return builder.as_markup()


def get_admin_game_control_keyboard(game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="🚀 Majburiy boshlash", callback_data=f"adm_force_start:{game_id}")
    builder.button(text="⏹ O'yinni to'xtatish", callback_data=f"adm_stop_game:{game_id}")
    builder.button(text="📋 Game Logs", callback_data=f"adm_logs:{game_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin_active_games")

    builder.adjust(2, 1, 1)
    return builder.as_markup()
