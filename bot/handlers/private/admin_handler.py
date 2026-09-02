"""
bot/handlers/private/admin_handler.py
Comprehensive Admin Panel handlers for BUNKER bot:
- /admin command
- Statistics dashboard (Users, Today, Games, Groups)
- Mandatory subscription (Channels management, FSM add channel, Delete channel, Toggle ON/OFF)
"""
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from bot.filters import IsAdmin
from database.repositories import UserRepository, GameRepository, ChannelRepository
from game.engine import GameEngine
from bot.keyboards.admin_kb import (
    get_admin_panel_keyboard, get_channels_management_keyboard,
    get_delete_channel_keyboard, get_back_to_admin_keyboard,
    get_admin_game_control_keyboard
)
from models.user import UserModel
from bot.config.settings import settings

router = Router()


class AddChannelStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_title = State()
    waiting_for_link = State()


# ==================== /admin COMMAND ====================

@router.message(Command("admin"))
async def cmd_admin_panel(
    message: Message,
    user: UserModel,
    user_repo: UserRepository,
    channel_repo: ChannelRepository,
    bot: Bot
):
    """Admin panel main entry point."""
    user_id = message.from_user.id
    is_admin = False

    # 1. Config ADMIN_IDS
    if settings.ADMIN_IDS and user_id in settings.ADMIN_IDS:
        is_admin = True

    # 2. Database admin flag
    if not is_admin:
        db_user = await user_repo.get_by_id(user_id)
        if db_user and db_user.is_admin:
            is_admin = True

    # 3. If no admins configured in settings and no admins in DB, auto-promote first caller!
    if not is_admin and not settings.ADMIN_IDS:
        admin_count = await user_repo.get_admin_count()
        if admin_count == 0:
            await user_repo.set_admin(user_id, True)
            is_admin = True

    # 4. In Group chats: check if user is Group Owner / Administrator
    if not is_admin and message.chat.type in ("group", "supergroup"):
        try:
            member = await bot.get_chat_member(message.chat.id, user_id)
            if member.status in ("creator", "administrator"):
                is_admin = True
        except Exception:
            pass

    if not is_admin:
        await message.reply(
            f"❌ <b>Kechirasiz, siz bot administratori emassiz!</b>\n"
            f"Sizning Telegram ID raqamingiz: <code>{user_id}</code>",
            parse_mode="HTML"
        )
        return

    sub_enabled = await channel_repo.is_mandatory_sub_enabled()
    kb = get_admin_panel_keyboard(sub_enabled=sub_enabled)

    text = (
        f"👑 <b>BUNKER BOT — ADMIN BOSHQARUV PANELI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Xush kelibsiz, <b>{message.from_user.first_name}</b>!\n\n"
        f"Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("setadmin"))
async def cmd_setadmin(message: Message, user_repo: UserRepository):
    """Assigns admin role to the user."""
    user_id = message.from_user.id
    await user_repo.set_admin(user_id, True)
    await message.reply(
        f"✅ <b>Siz muvaffaqiyatli Bot Administratori etib tayinlandingiz!</b>\n\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n\n"
        f"Endi <b>/admin</b> buyrug'ini yozib boshqaruv paneliga kirishingiz mumkin! 👑",
        parse_mode="HTML"
    )


# ==================== MAIN ADMIN NAVIGATION ====================

@router.callback_query(F.data == "admin_back_to_main")
async def cb_admin_back_to_main(callback: CallbackQuery, channel_repo: ChannelRepository, state: FSMContext):
    await state.clear()
    sub_enabled = await channel_repo.is_mandatory_sub_enabled()
    kb = get_admin_panel_keyboard(sub_enabled=sub_enabled)
    text = (
        f"👑 <b>BUNKER BOT — ADMIN BOSHQARUV PANELI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Quyidagi bo'limlardan birini tanlang:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "admin_close_panel")
async def cb_admin_close_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Admin panel yopildi.")


# ==================== 1. STATISTICS DASHBOARD ====================

@router.callback_query(F.data == "admin_view_stats")
async def cb_admin_view_stats(
    callback: CallbackQuery,
    user_repo: UserRepository,
    game_repo: GameRepository
):
    total_users = await user_repo.get_total_users_count()
    today_users = await user_repo.get_today_users_count()
    total_games = await game_repo.get_total_games_count()
    active_games = await game_repo.get_active_games_count()
    total_groups = await game_repo.get_total_groups_count()

    stats_text = (
        f"📊 <b>BOT STATISTIKASI (BUNKER GAME)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"• Jami a'zolar: <b>{total_users:,} ta</b>\n"
        f"• Bugun qo'shilganlar: <b>+{today_users:,} ta</b>\n\n"

        f"🎮 <b>O'yinlar & Guruhlar:</b>\n"
        f"• Jami o'ynalgan o'yinlar: <b>{total_games:,} ta</b>\n"
        f"• Ayni paytda faol o'yinlar: <b>{active_games:,} ta</b>\n"
        f"• Bot ulangan guruhlar soni: <b>{total_groups:,} ta</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )

    kb = get_back_to_admin_keyboard()
    try:
        await callback.message.edit_text(stats_text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


# ==================== 2. MANDATORY SUBSCRIPTION MANAGEMENT ====================

@router.callback_query(F.data == "admin_manage_channels")
async def cb_admin_manage_channels(callback: CallbackQuery, channel_repo: ChannelRepository, state: FSMContext):
    await state.clear()
    sub_enabled = await channel_repo.is_mandatory_sub_enabled()
    channels = await channel_repo.get_all_channels()

    status_icon = "🟢 YOQILGAN" if sub_enabled else "🔴 O'CHIRILGAN"
    
    lines = [
        f"📢 <b>MAJBURIY A'ZOLIK BOSHQARUVI</b>",
        f"Holati: <b>{status_icon}</b>\n",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"<b>📋 ULANISH MAJBURIY BO'LGAN KANALLAR:</b>\n"
    ]

    if channels:
        for idx, ch in enumerate(channels, 1):
            ch_status = "✅ Faol" if ch.get("is_active") else "⏸ To'xtatilgan"
            lines.append(f"{idx}. <b>{ch.get('title')}</b> ({ch.get('channel_id')})\n   └ Link: {ch.get('invite_link')} | {ch_status}")
    else:
        lines.append("<i>Hozircha majburiy kanallar qo'shilmagan.</i>")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")

    kb = get_channels_management_keyboard(channels=channels, sub_enabled=sub_enabled)
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "admin_toggle_mandatory_sub")
async def cb_admin_toggle_mandatory_sub(callback: CallbackQuery, channel_repo: ChannelRepository):
    current = await channel_repo.is_mandatory_sub_enabled()
    new_state = not current
    await channel_repo.set_mandatory_sub_enabled(new_state)

    status_str = "yoqildi 🟢" if new_state else "o'chirildi 🔴"
    await callback.answer(f"Majburiy a'zolik {status_str}!", show_alert=True)
    await cb_admin_manage_channels(callback, channel_repo, None)


# ==================== FSM: ADD CHANNEL ====================

@router.callback_query(F.data == "admin_add_channel")
async def cb_admin_add_channel_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddChannelStates.waiting_for_channel_id)
    text = (
        "➕ <b>YANGI MAJBURIY KANAL QO'SHISH</b>\n\n"
        "1-qadam: Kanal <b>username</b> yoki <b>ID</b>sini yuboring:\n\n"
        "<i>Misol: @bunker_yangiliklar yoki -100123456789</i>\n\n"
        "⚠️ <i>Eslatma: Bot ushbu kanalda <b>Admin</b> bo'lishi shart!</i>"
    )
    kb = get_back_to_admin_keyboard()
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.message(AddChannelStates.waiting_for_channel_id)
async def process_channel_id(message: Message, state: FSMContext, bot: Bot):
    channel_id = message.text.strip()
    
    # Try verifying bot is admin in channel
    try:
        chat = await bot.get_chat(channel_id)
        suggested_title = chat.title or channel_id
        suggested_link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else "")
        await state.update_data(channel_id=channel_id, title=suggested_title, link=suggested_link)
    except Exception as e:
        await message.reply(
            f"⚠️ <b>Ogohlantirish:</b> Bot ushbu kanalni tekshira olmadi ({e}).\n"
            f"Bot kanalda <b>Admin</b> ekanligiga ishonch hosil qiling.\n\n"
            f"Kanal nomini yuborishda davom etishingiz mumkin:",
            parse_mode="HTML"
        )
        await state.update_data(channel_id=channel_id)

    await state.set_state(AddChannelStates.waiting_for_title)
    await message.answer(
        "2-qadam: Kanal nomini yuboring (tugmada ko'rinadigan nom):\n"
        "<i>Misol: 📢 Bunker Rasmiy Kanali</i>",
        parse_mode="HTML"
    )


@router.message(AddChannelStates.waiting_for_title)
async def process_channel_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await state.set_state(AddChannelStates.waiting_for_link)
    await message.answer(
        "3-qadam: Kanalning taklif havolasini (Link) yuboring:\n"
        "<i>Misol: https://t.me/bunker_yangiliklar yoki https://t.me/+AbCdEf...</i>",
        parse_mode="HTML"
    )


@router.message(AddChannelStates.waiting_for_link)
async def process_channel_link(message: Message, state: FSMContext, channel_repo: ChannelRepository):
    link = message.text.strip()
    data = await state.get_data()
    channel_id = data.get("channel_id")
    title = data.get("title")

    success = await channel_repo.add_channel(channel_id=channel_id, title=title, invite_link=link)
    await state.clear()

    if success:
        await message.answer(
            f"✅ <b>Kanal muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📢 <b>Nomi:</b> {title}\n"
            f"🆔 <b>ID / User:</b> {channel_id}\n"
            f"🔗 <b>Link:</b> {link}",
            reply_markup=get_back_to_admin_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Kanalni saqlashda xatolik yuz berdi.",
            reply_markup=get_back_to_admin_keyboard(),
            parse_mode="HTML"
        )


# ==================== DELETE CHANNEL ====================

@router.callback_query(F.data == "admin_delete_channel_menu")
async def cb_admin_delete_channel_menu(callback: CallbackQuery, channel_repo: ChannelRepository):
    channels = await channel_repo.get_all_channels()
    if not channels:
        await callback.answer("O'chirish uchun kanallar mavjud emas.", show_alert=True)
        return

    kb = get_delete_channel_keyboard(channels)
    text = (
        "🗑 <b>QAYSI KANALNI O'CHIRMOQCHISIZ?</b>\n\n"
        "O'chirmoqchi bo'lgan kanalingiz tugmasini bosing:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("admin_do_delete_ch:"))
async def cb_admin_do_delete_ch(callback: CallbackQuery, channel_repo: ChannelRepository):
    ch_id = callback.data.split(":", 1)[1]
    await channel_repo.remove_channel(ch_id)
    await callback.answer("✅ Kanal majburiy ro'yxatdan o'chirildi!", show_alert=True)
    await cb_admin_manage_channels(callback, channel_repo, None)


# ==================== 3. ACTIVE GAMES MANAGEMENT ====================

@router.callback_query(F.data == "admin_active_games")
async def cb_admin_active_games(callback: CallbackQuery, game_engine: GameEngine):
    games = await game_engine.game_repo.get_active_games()
    if not games:
        text = "🎮 <b>Ayni paytda faol o'yinlar mavjud emas.</b>"
        kb = get_back_to_admin_keyboard()
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await callback.answer()
        return

    lines = ["🎮 <b>FAOL O'YINLAR RO'YXATI:</b>\n"]
    for g in games[:10]:
        players = await game_engine.player_repo.get_alive_players(g.id)
        lines.append(f"• <b>O'yin #{g.id}</b> | Holat: <code>{g.state}</code> | Tiriklar: <b>{len(players)} ta</b> | Chat: <code>{g.group_chat_id}</code>")

    lines.append("\n<i>Boshqarish uchun /stop_game yoki ID ni tanlang.</i>")

    kb = get_back_to_admin_keyboard()
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()
