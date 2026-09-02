"""
Private chat command handlers for BUNKER bot (/start, /profile, /help, /rules, /guide).
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


def get_private_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profilim", callback_data="show_my_profile")
    builder.button(text="🏅 Yutuqlarim", callback_data="show_my_achievements")
    builder.button(text="📚 Foydalanish qo'llanmasi", callback_data="show_bot_guide")
    builder.button(text="ℹ️ O'yin haqida", callback_data="show_about_game")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


@router.message(CommandStart(), IsPrivateChat())
async def cmd_start(message: Message, user_repo: UserRepository, user: UserModel):
    """Marks user as bot started and displays welcome panel."""
    await user_repo.set_bot_started(message.from_user.id)

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        f"🏢 <b>BUNKER — Telegram multiplayer strategik o'yiniga xush kelibsiz!</b>\n\n"
        f"✅ Endi siz Telegram guruhlarida <b>/bunker</b> o'yinlarida to'liq qatnasha olasiz.\n"
        f"🤫 O'yin davomida barcha maxfiy xususiyatlaringiz, qobiliyatlaringiz va maxfiy kartalaringiz aynan shu yerga yuboriladi.\n\n"
        f"<i>Quyidagi menyu orqali kerakli bo'limni tanlang:</i>"
    )

    await message.answer(welcome_text, reply_markup=get_private_main_keyboard(), parse_mode="HTML")


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
    builder.button(text="⬅️ Bosh menyu", callback_data="back_to_start")
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
    builder.button(text="⬅️ Bosh menyu", callback_data="back_to_start")
    builder.adjust(1)

    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "show_bot_guide")
async def cb_show_bot_guide(callback: CallbackQuery):
    """Detailed step-by-step guide on how to use the bot and play in groups."""
    guide_text = (
        "📚 <b>BOTDAN FOYDALANISH QO'LLANMASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>1️⃣ Botni guruhga qo'shish va Admin qilish:</b>\n"
        "• Botni do'stlaringiz bilan o'ynaydigan Telegram guruhga qo'shing.\n"
        "• Botga guruhda <b>Admin</b> huquqini bering *(ovoz berishda chatni yopish/ochish va xabarlarni Pin qilish uchun kerak)*.\n\n"

        "<b>2️⃣ O'yinni boshlash:</b>\n"
        "• Guruhda <b>/bunker</b> buyrug'ini yozing.\n"
        "• O'yinchilar <b>[🎮 O'yinga qo'shilish]</b> tugmasini bosadi.\n"
        "• <i>Muhim:</i> Har bir ishtirokchi botga shaxsiyda <b>/start</b> bosgan bo'lishi shart (kartalarini olish uchun).\n"
        "• Kamida 5 nafar o'yinchi yig'ilgach, <b>[🚀 O'yinni boshlash]</b> tugmasi bosiladi.\n\n"

        "<b>3️⃣ 1-bosqich: Xususiyat ochish (⏱ 30 sek):</b>\n"
        "• Guruh chati vaqtincha yopiladi.\n"
        "• Har bir o'yinchi 30 soniya ichida o'ziga ma'qul 1 ta xususiyatini (Kasb, Hobbi, Sog'liq va h.k.) ochadi.\n\n"

        "<b>4️⃣ 2-bosqich: Muhokama (⏱ 2 daqiqa):</b>\n"
        "• Guruh chati ochiladi!\n"
        "• O'yinchilar guruhda qizg'in bahslashadi: nega aynan ular bunkerda qolishi kerakligini isbotlaydi va kim xavfli/foydasiz ekanligini muhokama qiladi.\n\n"

        "<b>5️⃣ 3-bosqich: Ovoz berish (⏱ 60 sek):</b>\n"
        "• Guruh chati yana yopiladi.\n"
        "• O'yinchilar tugmalar orqali eng kam foydali nomzodga ovoz beradi. Eng ko'p ovoz olgan o'yinchi bunkerdan chiqariladi.\n\n"

        "<b>6️⃣ G'alaba va Yakuniy Tahlil:</b>\n"
        "• O'yinchilar soniga qarab (2, 3 yoki 4 kishi) g'oliblar qolguncha raundlar davom etadi.\n"
        "• Yakunda barcha g'oliblarning xususiyatlari Falokatga solishtirilib, haqiqiy <b>G'alaba</b> yoki <b>Yutqaziq</b> e'lon qilinadi!"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="ℹ️ O'yin haqida ma'lumot", callback_data="show_about_game")
    builder.button(text="⬅️ Bosh menyu", callback_data="back_to_start")
    builder.adjust(1)

    try:
        await callback.message.edit_text(guide_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "show_about_game")
async def cb_show_about_game(callback: CallbackQuery):
    """Detailed lore and game mechanics overview."""
    about_text = (
        "ℹ️ <b>BUNKER O'YINI HAQIDA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌍 <b>O'yin syujeti (Lore):</b>\n"
        "Yer yuzida global apokalipsis (halokat) sodir bo'ldi! Tirik qolishning yagona yo'li — mustahkam qutqaruv <b>BUNKERI</b>ga kirish.\n\n"

        "⚖️ <b>Bunker sig'imi (Dinamik):</b>\n"
        "Bunkerda resurslar va joy cheklangan:\n"
        "• <b>5 — 7 kishi bo'lsa:</b> 👉 2 ta g'olib qoladi\n"
        "• <b>8 — 14 kishi bo'lsa:</b> 👉 3 ta g'olib qoladi\n"
        "• <b>15 — 20 kishi bo'lsa:</b> 👉 4 ta g'olib qoladi\n\n"

        "🃏 <b>Xususiyatlar va Kartalar:</b>\n"
        "Har bir o'yinchiga tasodifiy xususiyatlar beriladi:\n"
        "• 👨‍💼 <b>Kasb:</b> Shifokor, Santexnik, Dengizchi, Musiqachi, Muhandis...\n"
        "• ❤️ <b>Sog'liq:</b> A'lo sog'lom, Shamollash, Saraton, Astma...\n"
        "• 🎒 <b>Inventar:</b> Suv filtri, Generator, Qurol, Dori-darmon, Gitara...\n"
        "• 🎓 <b>Bilim:</b> Tibbiyot, Qurilish, Qishloq xo'jaligi, Falsafa...\n"
        "• 🧠 <b>Xarakter</b> va 🧬 <b>Genetika</b>\n"
        "• ⚡ <b>Qobiliyatlar va Maxfiy kartalar:</b> Boshqalarning kartasini almashtirish, o'g'irlash, himoya qalqoni va h.k.\n\n"

        "🌋 <b>12 xil Falokat (Apokalipsis) turlari:</b>\n"
        "Yadro urushi, Suv toshqini, Zombi epidemiyasi, Yangi muzlik davri, Robotlar isyoni va boshqalar.\n\n"
        "<i>Har bir falokatda har xil kasb va buyumlar kerak bo'ladi!</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Foydalanish qo'llanmasi", callback_data="show_bot_guide")
    builder.button(text="⬅️ Bosh menyu", callback_data="back_to_start")
    builder.adjust(1)

    try:
        await callback.message.edit_text(about_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery):
    welcome_text = (
        f"👋 <b>Assalomu alaykum, {callback.from_user.first_name}!</b>\n\n"
        f"🏢 <b>BUNKER — Telegram multiplayer strategik o'yiniga xush kelibsiz!</b>\n\n"
        f"✅ Telegram guruhlarida <b>/bunker</b> o'yinlariga bemalol qo'shila olasiz.\n"
        f"<i>Quyidagi menyu orqali kerakli bo'limni tanlang:</i>"
    )
    try:
        await callback.message.edit_text(welcome_text, reply_markup=get_private_main_keyboard(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()
