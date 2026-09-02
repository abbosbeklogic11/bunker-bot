"""
Private chat command handlers for BUNKER bot (/start, /profile, /help, /rules, /guide).
Enforces mandatory subscription checks, deep-link joining, shop purchases, and referral system.
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
from bot.keyboards.shop_kb import get_shop_keyboard, get_shop_item_buy_keyboard, SHOP_ITEMS
from models.user import UserModel

router = Router()


def get_private_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Profilim", callback_data="show_my_profile")
    builder.button(text="🛒 Do'kon", callback_data="open_shop")
    builder.button(text="👥 Do'stlarni taklif qilish", callback_data="show_referral_panel")
    builder.button(text="🏅 Yutuqlarim", callback_data="show_my_achievements")
    builder.button(text="📚 Foydalanish qo'llanmasi", callback_data="show_bot_guide")
    builder.button(text="ℹ️ O'yin haqida", callback_data="show_about_game")
    builder.adjust(2, 2, 2)
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
    """Marks user as bot started, handles deep-link game join/referrals, checks mandatory sub, and displays welcome panel."""
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

    # 2. Check if user clicked referral link (/start ref_123456)
    if command.args and command.args.startswith("ref_"):
        try:
            referrer_id = int(command.args.replace("ref_", ""))
            if referrer_id != message.from_user.id:
                recorded = await user_repo.record_referral(
                    referrer_id=referrer_id,
                    referred_id=message.from_user.id,
                    bonus_coins=50,
                    bonus_diamonds=10,
                    newcomer_bonus_coins=30
                )
                if recorded:
                    try:
                        await bot.send_message(
                            chat_id=referrer_id,
                            text=(
                                f"🎉 <b>Ajoyib xabar!</b>\n"
                                f"Siz taklif qilgan do'stingiz <b>{message.from_user.first_name}</b> botga kirdi!\n\n"
                                f"💰 <b>+50 tanga</b> va 💎 <b>+10 brilliant</b> hisobingizga qo'shildi!"
                            ),
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
        except ValueError:
            pass

    # 3. Check if user clicked direct "O'yinga qo'shilish" deep-link (/start join_123)
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


# ==================== SHOP HANDLERS ====================

@router.callback_query(F.data == "open_shop")
async def cb_open_shop(callback: CallbackQuery, user_repo: UserRepository):
    """Renders the in-game store matching official layout."""
    user = await user_repo.get_by_id(callback.from_user.id)
    coins = user.coins if user else 0

    shop_text = (
        f"🛒 <b>DO'KON</b>\n\n"
        f"💵 <b>Pulingiz:</b> {coins}\n\n"
        f"<i>Kartani tanlang — tavsifi va narxi chiqadi.\n"
        f"Bir o'yinda faqat bitta maxsus karta ishlata olasiz. Sotib olingani ishlatilmaguncha saqlanib turadi.</i>"
    )

    try:
        await callback.message.edit_text(shop_text, reply_markup=get_shop_keyboard(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("shop_view:"))
async def cb_shop_view(callback: CallbackQuery, user_repo: UserRepository):
    """Shows details and buy button for a specific shop item."""
    code = callback.data.split(":")[1]
    item = next((it for it in SHOP_ITEMS if it["code"] == code), None)
    if not item:
        await callback.answer("Karta topilmadi.", show_alert=True)
        return

    user = await user_repo.get_by_id(callback.from_user.id)
    coins = user.coins if user else 0

    text = (
        f"{item['icon']} <b>{item['name'].upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Narxi:</b> {item['price']} tanga\n"
        f"💵 <b>Sizning balansingiz:</b> {coins} tanga\n\n"
        f"📝 <b>Tavsif:</b>\n{item['description']}\n\n"
        f"<i>Sotib olingan karta profilingiz inventarida saqlanadi va navbatdagi o'yinda ishlatish mumkin.</i>"
    )

    kb = get_shop_item_buy_keyboard(item["code"], item["price"])
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("shop_buy:"))
async def cb_shop_buy(callback: CallbackQuery, user_repo: UserRepository):
    """Executes item purchase."""
    code = callback.data.split(":")[1]
    item = next((it for it in SHOP_ITEMS if it["code"] == code), None)
    if not item:
        await callback.answer("Karta topilmadi.", show_alert=True)
        return

    res = await user_repo.buy_inventory_item(
        user_id=callback.from_user.id,
        item_code=item["code"],
        item_name=item["name"],
        cost=item["price"]
    )

    if not res.get("success"):
        err = res.get("error")
        if err == "INSUFFICIENT_FUNDS":
            user_coins = res.get("user_coins", 0)
            needed = item["price"] - user_coins
            await callback.answer(
                f"❌ Mablag' yetarli emas!\nBalansingiz: {user_coins} tanga.\nYana {needed} tanga kerak.",
                show_alert=True
            )
        else:
            await callback.answer("❌ Xaridni amalga oshirishda xatolik yuz berdi.", show_alert=True)
        return

    new_bal = res.get("new_balance", 0)
    await callback.answer(f"✅ {item['name']} sotib olindi! Qolgan balans: {new_bal} tanga.", show_alert=True)

    # Return to shop
    shop_text = (
        f"🛒 <b>DO'KON</b>\n\n"
        f"💵 <b>Pulingiz:</b> {new_bal}\n\n"
        f"<i>Kartani tanlang — tavsifi va narxi chiqadi.\n"
        f"Bir o'yinda faqat bitta maxsus karta ishlata olasiz. Sotib olingani ishlatilmaguncha saqlanib turadi.</i>"
    )
    try:
        await callback.message.edit_text(shop_text, reply_markup=get_shop_keyboard(), parse_mode="HTML")
    except Exception:
        pass


# ==================== REFERRAL HANDLERS ====================

@router.callback_query(F.data == "show_referral_panel")
async def cb_show_referral_panel(callback: CallbackQuery, user_repo: UserRepository, bot: Bot):
    """Displays referral link and statistics."""
    bot_info = await bot.get_me()
    uid = callback.from_user.id
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{uid}"
    stats = await user_repo.get_referral_stats(uid)

    text = (
        f"👥 <b>DO'STLARNI TAKLIF QILISH (REFERAL TIZIMI)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Do'stlaringizni botga taklif qiling va har bir taklif qilingan do'stingiz uchun mukofot oling!\n\n"
        f"🎁 <b>Mukofotlar:</b>\n"
        f"• Sizga: 💰 <b>+50 tanga</b> va 💎 <b>+10 brilliant</b>\n"
        f"• Do'stingizga: 💰 <b>+30 tanga</b> xush kelibsiz bonusi!\n\n"
        f"🔗 <b>Sizning shaxsiy referal havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"📊 <b>Sizning referal statistikangiz:</b>\n"
        f"• Taklif qilingan do'stlar: <b>{stats['total_referrals']} ta</b>\n"
        f"• Ishlangan tangalar: <b>{stats['earned_coins']} 💰</b>\n"
        f"• Ishlangan brilliantlar: <b>{stats['earned_diamonds']} 💎</b>"
    )

    share_text = f"🏢 Bunker multiplayer o'yinini birga o'ynaymiz! Havola orqali kiring va 30 tanga bonus oling: {ref_link}"
    import urllib.parse
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(ref_link)}&text={urllib.parse.quote('Bunker o\'yiniga taklifnoma! 🏢')}"

    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Do'stlarga ulashish", url=share_url)
    builder.button(text="🛒 Do'kon", callback_data="open_shop")
    builder.button(text="⬅️ Bosh menyu", callback_data="back_to_start")
    builder.adjust(1, 2)

    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


# ==================== PROFILE & ACHIEVEMENTS ====================

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
    inventory = await user_repo.get_user_inventory(user.id)
    text = format_profile(user.model_dump(), achievements)
    
    if inventory:
        inv_lines = ["\n🎒 <b>Maxsus kartalaringiz (Inventar):</b>"]
        for inv in inventory:
            inv_lines.append(f"• <b>{inv['item_name']}</b> ({inv['quantity']} dona)")
        text += "\n" + "\n".join(inv_lines)

    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Do'kon", callback_data="open_shop")
    builder.button(text="👥 Referal", callback_data="show_referral_panel")
    builder.button(text="🏅 Yutuqlarim", callback_data="show_my_achievements")
    builder.button(text="⬅️ Bosh menyu", callback_data="back_to_start")
    builder.adjust(2, 2)

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
        "• O'yinchilar <b>[🎮 O'yinga qo'shilish]</b> tugmasini bosadi va avtomatik o'yinga ulanadi.\n"
        "• Kamida 5 nafar o'yinchi yig'ilgach, <b>[🚀 O'yinni boshlash]</b> tugmasi bosiladi.\n\n"

        "<b>3️⃣ 1-bosqich: Xususiyat ochish (⏱ 1.5 daqiqa):</b>\n"
        "• Guruh chati vaqtincha yopiladi.\n"
        "• Har bir o'yinchi 1.5 daqiqa (90 soniya) ichida o'ziga ma'qul 1 ta xususiyatini (Kasb, Hobbi, Sog'liq va h.k.) ochadi.\n\n"

        "<b>4️⃣ 2-bosqich: Muhokama (⏱ 2-5 daqiqa):</b>\n"
        "• Guruh chati ochiladi!\n"
        "• O'yinchilar soniga qarab muhokama vaqti beriladi (5-8 kishi: 2 daq, 8-10 kishi: 3 daq, 10-15 kishi: 4 daq, 15-20 kishi: 5 daq).\n\n"

        "<b>5️⃣ 3-bosqich: Ovoz berish (⏱ 60 sek):</b>\n"
        "• Guruh chati yana yopiladi.\n"
        "• O'yinchilar tugmalar orqali ovoz beradi. Har bir nomzodda to'plangan ovozlar real vaqtda jonli ko'rinib turadi.\n\n"

        "<b>6️⃣ G'alaba va Mukofotlar:</b>\n"
        "• Bunker sig'imiga qarab g'oliblar qolgach, barcha g'oliblarga 💰 tangalar va 💎 brilliantlar beriladi!"
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
        "• ⚡ <b>Qobiliyatlar va Do'kon kartalari:</b> Haydashdan himoya, 2x ovoz, Josus, Fosh qilish...\n\n"

        "🌋 <b>12 xil Falokat (Apokalipsis) turlari:</b>\n"
        "Yadro urushi, Suv toshqini, Zombi epidemiyasi, Yangi muzlik davri, Robotlar isyoni va boshqalar."
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
