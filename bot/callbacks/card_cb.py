"""
Card execution callbacks for Private chat in BUNKER game.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from game.engine import GameEngine
from bot.keyboards.ability_kb import get_player_cards_keyboard, get_card_target_keyboard

router = Router()


@router.callback_query(F.data.startswith("mygame_cards:"))
async def handle_show_cards_list(callback: CallbackQuery, game_engine: GameEngine):
    game_id = int(callback.data.split(":")[1])
    cards = await game_engine.player_repo.get_player_cards(game_id, callback.from_user.id)
    
    if not cards:
        await callback.answer("Sizda maxfiy kartalar yo'q.", show_alert=True)
        return

    kb = get_player_cards_keyboard(game_id, cards)
    await callback.message.edit_text(
        "🃏 <b>SIZNING MAXFIY KARTALARINGIZ:</b>\nIshlatmoqchi bo'lgan kartangizni tanlang:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("use_card_select:"))
async def handle_card_select(callback: CallbackQuery, game_engine: GameEngine):
    parts = callback.data.split(":")
    game_id = int(parts[1])
    player_card_id = int(parts[2])

    alive = await game_engine.player_repo.get_alive_players(game_id)
    alive_data = []
    for p in alive:
        u = await game_engine.user_repo.get_by_id(p.user_id)
        alive_data.append({"user_id": p.user_id, "name": u.first_name if u else f"O'yinchi #{p.user_id}"})

    kb = get_card_target_keyboard(game_id, player_card_id, alive_data)
    await callback.message.edit_text(
        "🎯 <b>Kartani kimga qo'llamoqchisiz?</b>\nNishonni tanlang yoki 'O'zimga ishlatish'ni bosing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("use_card_target:"))
async def handle_card_target(callback: CallbackQuery, game_engine: GameEngine):
    parts = callback.data.split(":")
    game_id = int(parts[1])
    player_card_id = int(parts[2])
    target_id = int(parts[3]) if int(parts[3]) != 0 else None

    res = await game_engine.use_card(game_id, callback.from_user.id, player_card_id, target_id)
    msg = res.get("message", "Karta ishlatildi.")

    await callback.answer(msg, show_alert=True)

    # Return to cards list
    cards = await game_engine.player_repo.get_player_cards(game_id, callback.from_user.id)
    kb = get_player_cards_keyboard(game_id, cards)
    try:
        await callback.message.edit_text(
            f"🃏 <b>Maxfiy kartalaringiz:</b>\n<i>{msg}</i>",
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception:
        pass
