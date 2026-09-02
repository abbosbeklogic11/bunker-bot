"""
Game dashboard interaction callbacks for BUNKER game.
"""
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from game.engine import GameEngine
from utils.formatters import format_player_list, format_attributes_by_type, format_dashboard
from bot.keyboards.game_kb import get_game_dashboard_keyboard, get_back_to_game_keyboard
from bot.keyboards.voting_kb import get_voting_keyboard
from bot.keyboards.reveal_kb import ATTR_NAMES
from models.user import UserModel

router = Router()


@router.callback_query(F.data.startswith("game_view_players:"))
async def handle_game_view_players(callback: CallbackQuery, game_engine: GameEngine):
    game_id = int(callback.data.split(":")[1])
    players = await game_engine.player_repo.get_all_players(game_id)
    
    players_data = []
    for p in players:
        u = await game_engine.user_repo.get_by_id(p.user_id)
        players_data.append({
            "name": u.first_name if u else "O'yinchi",
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
            "is_protected": p.is_protected
        })

    text = format_player_list(players_data)
    kb = get_back_to_game_keyboard(game_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("game_attr:"))
async def handle_game_attr_view(callback: CallbackQuery, game_engine: GameEngine):
    parts = callback.data.split(":")
    game_id = int(parts[1])
    attr_type = parts[2]

    revealed_data = await game_engine.player_repo.get_revealed_attributes_by_type(game_id, attr_type)
    if not revealed_data:
        await callback.answer("🔒 Bu xususiyat hali ochilmagan!", show_alert=True)
        return

    text = format_attributes_by_type(attr_type, revealed_data)
    kb = get_back_to_game_keyboard(game_id)

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("reveal_attr:"))
async def handle_reveal_attr(callback: CallbackQuery, game_engine: GameEngine):
    """Processes a player's request to reveal a specific attribute."""
    parts = callback.data.split(":")
    game_id = int(parts[1])
    attr_type = parts[2]
    user_id = callback.from_user.id

    res = await game_engine.player_reveal_attribute(game_id, user_id, attr_type)
    if not res.get("success"):
        await callback.answer(res.get("message", "Xatolik yuz berdi."), show_alert=True)
        return

    attr_val = res["attribute"].attribute_value
    attr_label = ATTR_NAMES.get(attr_type, attr_type.title())
    await callback.answer(
        f"✅ Siz o'zingizning {attr_label} xususiyatingizni ochdingiz:\n👉 {attr_val}",
        show_alert=True
    )


@router.callback_query(F.data.startswith("game_open_voting:"))
async def handle_game_open_voting(callback: CallbackQuery, game_engine: GameEngine):
    game_id = int(callback.data.split(":")[1])
    game = await game_engine.game_repo.get_by_id(game_id)
    
    if not game or game.state not in ("VOTING", "DUEL"):
        await callback.answer("⏳ Hozir ovoz berish bosqichi emas!", show_alert=True)
        return

    alive = await game_engine.player_repo.get_alive_players(game_id)
    alive_data = []
    for p in alive:
        u = await game_engine.user_repo.get_by_id(p.user_id)
        alive_data.append({"user_id": p.user_id, "name": u.first_name if u else f"O'yinchi #{p.user_id}"})

    kb = get_voting_keyboard(game_id, alive_data, voter_id=callback.from_user.id)
    try:
        await callback.message.edit_text(
            "🗳 <b>KIMNI BUNKERDAN CHIQARAMIZ?</b>\nO'zingiz nomzod deb hisoblagan o'yinchiga ovoz bering:",
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("game_back:"))
async def handle_game_back_to_dashboard(callback: CallbackQuery, game_engine: GameEngine):
    game_id = int(callback.data.split(":")[1])
    d_data = await game_engine.get_game_dashboard_data(game_id)
    
    if not d_data:
        await callback.answer("O'yin topilmadi.", show_alert=True)
        return

    text = format_dashboard(
        round_num=d_data["round"],
        phase=d_data["phase"],
        time_left=d_data["time_left"],
        apocalypse=d_data["apocalypse"],
        bunker={},
        alive_count=d_data["alive_count"],
        total_count=d_data["total_count"],
        capacity=d_data["capacity"],
        revealed_types=d_data["revealed_types"]
    )
    kb = get_game_dashboard_keyboard(game_id, d_data["revealed_types"], d_data["phase"])

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("game_private_abilities:"))
async def handle_game_private_abilities(callback: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    await callback.answer(
        f"⚡ Qobiliyatlarni ishlatish uchun @{bot_info.username} shaxsiy chatiga o'ting!",
        show_alert=True
    )


@router.callback_query(F.data.startswith("game_private_cards:"))
async def handle_game_private_cards(callback: CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    await callback.answer(
        f"🃏 Maxfiy kartalarni ko'rish uchun @{bot_info.username} shaxsiy chatiga o'ting!",
        show_alert=True
    )


@router.callback_query(F.data.startswith("game_rules:"))
async def handle_game_rules(callback: CallbackQuery):
    rules_text = (
        "📖 <b>BUNKER O'YINI QOIDALARI:</b>\n\n"
        "• Har raundda o'z xususiyatlaringiz bilan o'zingizni himoya qiling.\n"
        "• Guruhda bahslashib, keraksiz deb topilgan nomzodga ovoz bering.\n"
        "• Private chatda qobiliyat va maxfiy kartalarni o'z vaqtida qo'llang!\n"
        "• Faqat 4 ta eng foydali o'yinchi bunkerga kirib g'olib bo'ladi!"
    )
    game_id = int(callback.data.split(":")[1]) if ":" in callback.data else 0
    kb = get_back_to_game_keyboard(game_id)

    try:
        await callback.message.edit_text(rules_text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("game_stop:"))
async def handle_game_stop_button(callback: CallbackQuery, game_engine: GameEngine, user: UserModel, bot: Bot):
    game_id = int(callback.data.split(":")[1])
    game = await game_engine.game_repo.get_by_id(game_id)
    if not game:
        await callback.answer("O'yin topilmadi.", show_alert=True)
        return

    # Check permission: Creator, Bot Admin, or Group Admin
    is_allowed = (game.created_by == user.id) or user.is_admin
    if not is_allowed and callback.message.chat:
        try:
            member = await bot.get_chat_member(callback.message.chat.id, user.id)
            if member.status in ("creator", "administrator"):
                is_allowed = True
        except Exception:
            pass

    if not is_allowed:
        await callback.answer("❌ Faqat o'yin yaratuvchisi yoki guruh admini o'yinni to'xtata oladi!", show_alert=True)
        return

    await game_engine.game_repo.finish_game(game_id)
    await game_engine.timer_engine.cancel_timer(game_id)

    try:
        await callback.message.edit_text(
            f"⏹ <b>BUNKER O'YINI #{game_id} TO'XTATILDI.</b>\n\n"
            f"To'xtatuvchi: <b>{user.display_name}</b>\n"
            f"Yangi o'yin boshlash uchun /bunker yuboring.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer("O'yin to'xtatildi.", show_alert=False)
