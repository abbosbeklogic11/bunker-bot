"""
Lobby callbacks handler for BUNKER game.
Processes join, start, cancel, rules, and player list requests from the group chat lobby.
"""
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from game.engine import GameEngine
from utils.formatters import format_lobby_message
from bot.keyboards.lobby_kb import get_lobby_keyboard
from models.user import UserModel

router = Router()


@router.callback_query(F.data.startswith("lobby_join:"))
async def handle_lobby_join(callback: CallbackQuery, game_engine: GameEngine, user: UserModel, bot: Bot):
    game_id = int(callback.data.split(":")[1])
    
    # 1. Ensure user has started the bot privately
    if not user.is_bot_started:
        bot_info = await bot.get_me()
        await callback.answer(
            f"❌ Avval botni shaxsiy chatda ishga tushiring!\n@{bot_info.username} ga /start yuboring.",
            show_alert=True
        )
        return

    # 2. Join game
    result = await game_engine.join_game(game_id, callback.from_user.id)
    if not result.get("success"):
        err = result.get("error")
        if err == "LOBBY_FULL":
            await callback.answer("❌ Lobby to'lgan (20/20)!", show_alert=True)
        elif err == "NOT_IN_LOBBY":
            await callback.answer("❌ O'yin allaqachon boshlangan yoki tugagan!", show_alert=True)
        else:
            await callback.answer("❌ O'yinga qo'shilishda xatolik yuz berdi.", show_alert=True)
        return

    # 3. Update lobby message
    players = await game_engine.player_repo.get_all_players(game_id)
    players_data = []
    for p in players:
        u = await game_engine.user_repo.get_by_id(p.user_id)
        players_data.append({"name": u.first_name if u else "O'yinchi", "first_name": u.first_name if u else ""})

    text = format_lobby_message(game_id, players_data, max_players=game_engine.config.MAX_PLAYERS, min_players=game_engine.config.MIN_PLAYERS)
    kb = get_lobby_keyboard(game_id, len(players_data), max_players=game_engine.config.MAX_PLAYERS)

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer("✅ Siz o'yinga muvaffaqiyatli qo'shildingiz!", show_alert=False)


@router.callback_query(F.data.startswith("lobby_players:"))
async def handle_lobby_players(callback: CallbackQuery, game_engine: GameEngine):
    game_id = int(callback.data.split(":")[1])
    players = await game_engine.player_repo.get_all_players(game_id)
    
    names = []
    for idx, p in enumerate(players, 1):
        u = await game_engine.user_repo.get_by_id(p.user_id)
        n = u.first_name if u else f"#{p.user_id}"
        names.append(f"{idx}. {n}")

    text = "👥 O'YINCHILAR:\n" + "\n".join(names[:10])
    if len(names) > 10:
        text += f"\n...va yana {len(names)-10} kishi"

    await callback.answer(text[:190], show_alert=True)


@router.callback_query(F.data.startswith("lobby_rules:"))
async def handle_lobby_rules(callback: CallbackQuery):
    rules_alert = (
        "📖 BUNKER QOIDALARI:\n"
        "• 5-20 o'yinchi ishtirok etadi\n"
        "• Faqat 4 kishi omon qolib g'olib bo'ladi\n"
        "• Maxfiy kartalar shaxsiy chatga yuboriladi\n"
        "• Ovoz berishda kam ovoz olib, oxirigacha turing!"
    )
    await callback.answer(rules_alert, show_alert=True)


@router.callback_query(F.data.startswith("lobby_start:"))
async def handle_lobby_start(callback: CallbackQuery, game_engine: GameEngine, user: UserModel):
    game_id = int(callback.data.split(":")[1])
    game = await game_engine.game_repo.get_by_id(game_id)
    
    if not game:
        await callback.answer("❌ O'yin topilmadi!", show_alert=True)
        return

    # Check permission
    if game.created_by != user.id and not user.is_admin:
        await callback.answer("❌ Faqat yaratuvchi yoki admin boshlay oladi!", show_alert=True)
        return

    res = await game_engine.start_game(game_id, by_user_id=user.id)
    if not res.get("success"):
        err = res.get("error")
        if err == "NOT_ENOUGH_PLAYERS":
            await callback.answer(f"❌ Kamida {res.get('min')} ta o'yinchi kerak!", show_alert=True)
        else:
            await callback.answer("❌ O'yinni boshlashda xatolik yuz berdi.", show_alert=True)
        return

    await callback.answer("🚀 O'yin boshlanmoqda!", show_alert=False)


@router.callback_query(F.data.startswith("lobby_cancel:"))
async def handle_lobby_cancel(callback: CallbackQuery, game_engine: GameEngine, user: UserModel):
    game_id = int(callback.data.split(":")[1])
    game = await game_engine.game_repo.get_by_id(game_id)
    
    if not game:
        await callback.answer("❌ O'yin topilmadi!", show_alert=True)
        return

    if game.created_by != user.id and not user.is_admin:
        await callback.answer("❌ Faqat yaratuvchi o'yinni bekor qila oladi!", show_alert=True)
        return

    await game_engine.cancel_game(game_id, by_user_id=user.id)
    try:
        await callback.message.edit_text("❌ <b>Bunker o'yini bekor qilindi.</b>", parse_mode="HTML")
    except Exception:
        pass
    await callback.answer("O'yin bekor qilindi.", show_alert=False)
