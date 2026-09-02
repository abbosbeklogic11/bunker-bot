"""
Private chat command handlers for BUNKER bot (/start, /profile, /help, /rules, /guide).
Enforces mandatory subscription checks and supports direct deep-link joining from groups.
"""
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.filters import IsPrivateChat
from database.repositories import UserRepository, AchievementRepository, ChannelRepository
from game.engine import GameEngine
from services.subscription_service import SubscriptionService
from utils.formatters import format_profile, format_lobby_message
from bot.keyboards.lobby_kb import get_lobby_keyboard
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
async def cmd_start(
    message: Message,
    command: CommandObject,
    user_repo: UserRepository,
    channel_repo: ChannelRepository,
    game_engine: GameEngine,
    user: UserModel,
    bot: Bot
):
    """Marks user as bot started, handles deep-link game join, checks mandatory sub, and displays welcome panel."""
    await user_repo.set_bot_started(message.from_user.id)

    # 1. Check Mandatory Subscription
    is_subscribed, unjoined = await SubscriptionService.check_user_subscription(bot, message.from_user.id, channel_repo)
    if not is_subscribed and unjoined:
        kb = SubscriptionService.get_subscription_keyboard(unjoined)
        sub_text = (
            f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
            f"⚠️ <b>Botdan to'liq foydalanish va guruhlarda o'yinga qo'shilish uchun rasmiy homiy kanallarimizga a'zo bo'ling:</b>\n\n"
            f"<i>Barcha kanallarga a'zo bo'lgach, '✅ A'zolikni tekshirish' tugmasini bosing:</i>"
        )
        await message.answer(sub_text, reply_markup=kb, parse_mode="HTML")
        return

    # 2. Check if user clicked direct "O'yinga qo'shilish" deep-link (e.g. /start join_123)
    if command.args and command.args.startswith("join_"):
        try:
            game_id = int(command.args.replace("join_", ""))
        except ValueError:
            game_id = None

        if game_id:
            join_res = await game_engine.join_game(game_id, message.from_user.id)
            if join_res.get("success"):
                # Update group lobby message
                players = await game_engine.player_repo.get_all_players(game_id)
                players_data = []
                for p in players:
                    u = await game_engine.user_repo.get_by_id(p.user_id)
                    players_data.append({"name": u.first_name if u else "O'yinchi", "first_name": u.first_name if u else ""})
                
                game = await game_engine.game_repo.get_by_id(game_id)
                if game and game.dashboard_message_id:
                    bot_info = await bot.get_me()
                    text = format_lobby_message(game_id, players_data, max_players=game_engine.config.MAX_PLAYERS, min_players=game_engine.config.MIN_PLAYERS)
                    kb = get_lobby_keyboard(game_id, len(players_data), max_players=game_engine.config.MAX_PLAYERS, bot_username=bot_info.username)
                    try:
                        await bot.edit_message_text(chat_id=game.group_chat_id, message_id=game.dashboard_message_id, text=text, reply_markup=kb, parse_mode="HTML")
                    except Exception:
                        pass

                msg = (
                    f"🎉 <b>Tabriklaymiz, {message.from_user.first_name}!</b>\n\n"
                    f"✅ <b>Siz #{game_id}-sonli Bunker o'yiniga muvaffaqiyatli qo'shildingiz!</b>\n\n"
                    f"📍 <i>Guruhga qaytib o'yin boshlanishini kuting. Barcha maxfiy xususiyatlaringiz shu yerga yuboriladi.</i>"
                )
                await message.answer(msg, reply_markup=get_private_main_keyboard(), parse_mode="HTML")
                return
            else:
                err = join_res.get("error")
                if err == "ALREADY_JOINED":
                    msg = f"ℹ️ <b>Siz allaqachon #{game_id}-sonli o'yinga qo'shilgansiz!</b>\nGuruhga qaytib o'yinni kuting."
                elif err == "LOBBY_FULL":
                    msg = f"❌ <b>#{game_id}-sonli o'yin lobby'si to'lgan (20/20)!</b>"
                elif err == "NOT_IN_LOBBY":
                    msg = f"❌ <b>#{game_id}-sonli o'yin allaqachon boshlangan yoki yakunlangan!</b>"
                else:
                    msg = f"❌ <b>O'yinga qo'shilishda xatolik yuz berdi.</b>"
                await message.answer(msg, reply_markup=get_private_main_keyboard(), parse_mode="HTML")
                return

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        f"🏢 <b>BUNKER — Telegram multiplayer strategik o'yiniga xush kelibsiz!</b>\n\n"
        f"✅ Endi siz Telegram guruhlarida <b>/bunker</b> o'yinlarida to'liq qatnasha olasiz.\n"
        f"🤫 O'yin davomida barcha maxfiy xususiyatlaringiz, qobiliyatlaringiz va maxfiy kartalaringiz aynan shu yerga yuboriladi.\n\n"
        f"<i>Quyidagi menyu orqali kerakli bo'limni tanlang:</i>"
    )

    await message.answer(welcome_text, reply_markup=get_private_main_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "check_subscription_status")
async def cb_check_subscription_status(
    callback: CallbackQuery,
    channel_repo: ChannelRepository,
    bot: Bot
):
    """Verifies user's subscription on demand."""
    is_subscribed, unjoined = await SubscriptionService.check_user_subscription(bot, callback.from_user.id, channel_repo)
    if not is_subscribed and unjoined:
        kb = SubscriptionService.get_subscription_keyboard(unjoined)
        try:
            await callback.message.edit_reply_markup(reply_markup=kb)
        except Exception:
            pass
        await callback.answer("❌ Siz hali barcha kanallarga a'zo bo'lmadingiz! Iltimos, barcha kanallarga a'zo bo'ling.", show_alert=True)
        return

    welcome_text = (
        f"🎉 <b>A'zolik muvaffaqiyatli tasdiqlandi!</b>\n\n"
        f"🏢 <b>BUNKER multiplayer o'yiniga xush kelibsiz!</b>\n\n"
        f"✅ Endi siz Telegram guruhlarida <b>/bunker</b> o'yinlarida bemalol qatnasha olasiz."
    )
    try:
        await callback.message.edit_text(welcome_text, reply_markup=get_private_main_keyboard(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("✅ A'zolik tasdiqlandi!")


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

        "<b>3️⃣ 1-bosqich: Xususiyat ochish (⏱ 1.5 daqiqa):</b>\n"
        "• Guruh chati vaqtincha yopiladi.\n"
        "• Har bir o'yinchi 1.5 daqiqa (90 soniya) ichida o'ziga ma'qul 1 ta xususiyatini (Kasb, Hobbi, Sog'liq va h.k.) ochadi.\n\n"

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
