"""
Admin management keyboards for BUNKER game.
Provides complete navigation for Statistics, Mandatory Channels, Active Games, and Bot Controls.
"""
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_panel_keyboard(sub_enabled: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    sub_status = "🟢 Yoqilgan" if sub_enabled else "🔴 O'chirilgan"
    builder.button(text="📊 To'liq Statistika", callback_data="admin_view_stats")
    builder.button(text=f"📢 Majburiy A'zolik ({sub_status})", callback_data="admin_manage_channels")
    builder.button(text="🎮 Faol O'yinlar", callback_data="admin_active_games")
    builder.button(text="❌ Menyuni yopish", callback_data="admin_close_panel")

    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


# Backward-compatible alias
get_admin_menu_keyboard = get_admin_panel_keyboard


def get_channels_management_keyboard(channels: List[Dict[str, Any]], sub_enabled: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    toggle_text = "🔴 Majburiy a'zolikni o'chirish" if sub_enabled else "🟢 Majburiy a'zolikni yoqish"
    builder.button(text=toggle_text, callback_data="admin_toggle_mandatory_sub")
    builder.button(text="➕ Yangi kanal qo'shish", callback_data="admin_add_channel")

    if channels:
        builder.button(text="🗑 Kanalni o'chirish", callback_data="admin_delete_channel_menu")

    builder.button(text="⬅️ Admin panelga qaytish", callback_data="admin_back_to_main")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def get_delete_channel_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for ch in channels:
        ch_id = ch.get("channel_id")
        title = ch.get("title", f"Kanal {ch_id}")
        builder.button(text=f"❌ {title}", callback_data=f"admin_do_delete_ch:{ch_id}")

    builder.button(text="⬅️ Orqaga", callback_data="admin_manage_channels")
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Admin panelga qaytish", callback_data="admin_back_to_main")
    return builder.as_markup()


def get_admin_game_control_keyboard(game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="🚀 Majburiy boshlash", callback_data=f"adm_force_start:{game_id}")
    builder.button(text="⏹ O'yinni to'xtatish", callback_data=f"adm_stop_game:{game_id}")
    builder.button(text="📋 Game Logs", callback_data=f"adm_logs:{game_id}")
    builder.button(text="⬅️ Orqaga", callback_data="admin_active_games")

    builder.adjust(2, 1, 1)
    return builder.as_markup()
