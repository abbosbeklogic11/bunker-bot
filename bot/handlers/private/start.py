"""
Private chat command handlers for BUNKER bot (/start, /profile, /help).
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.filters import IsPrivateChat
from database.repositories import UserRepository, AchievementRepository
from utils.formatters import format_profile
from models.user import UserModel

router = Router()


@router.message(CommandStart(), IsPrivateChat())
async def cmd_start(message: Message, user_repo: UserRepository, user: UserModel):
    """Marks user as bot started and displays welcome panel."""
    await user_repo.set_bot_started(message.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profilim", callback_data="show_my_profile")
    builder.button(text="🏅 Yutuqlarim", callback_data="show_my_achievements")
    builder.button(text="📖 O'yin qoidalari", callback_data="show_private_rules")
    builder.adjust(2, 1)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        f"🏢 <b>BUNKER multiplayer o'yin platformasiga xush kelibsiz!</b>\n\n"
        f"✅ Endi siz Telegram guruhlarida <b>/bunker</b> o'yinlariga bemalol qo'shila olasiz.\n"
        f"🤫 O'yin davomida barcha maxfiy kartalaringiz va qobiliyatlaringiz aynan shu yerga (Private) yuboriladi.\n\n"
        f"<i>Profil va yutuqlaringizni ko'rish uchun pastdagi tugmalardan foydalaning!</i>"
    )

    await message.answer(welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.message(Command("profile"), IsPrivateChat())
async def cmd_profile(message: Message, user_repo: UserRepository, achievement_repo: AchievementRepository):
    """Displays player profile and stats."""
    user = await user_repo.get_by_id(message.from_user.id)
    if not user:
        await message.reply("Foydalanuvchi topilmadi.")
        return

    achievements = await achievement_repo.get_user_achievements(user.id)
    text = format_profile(user.model_dump(), achievements)
    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "show_my_profile")
async def cb_show_my_profile(callback: CallbackQuery, user_repo: UserRepository, achievement_repo: AchievementRepository):
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    achievements = await achievement_repo.get_user_achievements(user.id)
    text = format_profile(user.model_dump(), achievements)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏅 Yutuqlarim", callback_data="show_my_achievements")
    builder.button(text="⬅️ Bosh sahifa", callback_data="back_to_start")
    builder.adjust(1)

    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "show_my_achievements")
async def cb_show_my_achievements(callback: CallbackQuery, achievement_repo: AchievementRepository):
    achievements = await achievement_repo.get_user_achievements(callback.from_user.id)
    
    lines = ["🏅 <b>SIZNING YUTUQLARINGIZ (ACHIEVEMENTS):</b>\n"]
    if achievements:
        for a in achievements:
            lines.append(f"{a.get('icon', '⭐')} <b>{a.get('name')}</b> — <i>{a.get('description')}</i>")
    else:
        lines.append("<i>Siz hali yutuqlarga ega emassiz. O'yinlarda g'alaba qozonib yutuqlarni oching!</i>")

    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profilga qaytish", callback_data="show_my_profile")
    builder.adjust(1)

    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "show_private_rules")
async def cb_show_private_rules(callback: CallbackQuery):
    rules_text = (
        "📖 <b>BUNKER O'YINI HAQIDA:</b>\n\n"
        "• Bunker — 5 dan 20 gacha o'yinchi ishtirok etadigan real-time multiplayer strategik o'yin.\n"
        "• Maqsad: 4 ta eng foydali tirik qoluvchilar safiga kirish.\n"
        "• Guruhda /bunker yozib o'yin boshlang!\n"
        "• Barcha maxfiy xususiyatlaringizni bot sizga yuboradi."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Bosh sahifa", callback_data="back_to_start")
    builder.adjust(1)

    try:
        await callback.message.edit_text(rules_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profilim", callback_data="show_my_profile")
    builder.button(text="🏅 Yutuqlarim", callback_data="show_my_achievements")
    builder.button(text="📖 O'yin qoidalari", callback_data="show_private_rules")
    builder.adjust(2, 1)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {callback.from_user.first_name}!</b>\n\n"
        f"🏢 <b>BUNKER multiplayer o'yin platformasiga xush kelibsiz!</b>\n\n"
        f"✅ Telegram guruhlarida <b>/bunker</b> o'yinlariga bemalol qo'shila olasiz."
    )
    try:
        await callback.message.edit_text(welcome_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()
