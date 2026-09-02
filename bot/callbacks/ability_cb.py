"""
Ability execution callbacks for Private chat in BUNKER game.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from game.engine import GameEngine
from bot.keyboards.ability_kb import get_ability_target_keyboard, get_player_abilities_keyboard

router = Router()


@router.callback_query(F.data.startswith("mygame_abilities:"))
async def handle_show_abilities_list(callback: CallbackQuery, game_engine: GameEngine):
    game_id = int(callback.data.split(":")[1])
    abilities = await game_engine.player_repo.get_player_abilities(game_id, callback.from_user.id)
    
    if not abilities:
        await callback.answer("Sizda maxsus qobiliyat yo'q.", show_alert=True)
        return

    kb = get_player_abilities_keyboard(game_id, abilities)
    await callback.message.edit_text(
        "⚡ <b>SIZNING QOBILIYATLARINGIZ:</b>\nIshlatmoqchi bo'lgan qobiliyatingizni tanlang:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("use_ab_select:"))
async def handle_ability_select(callback: CallbackQuery, game_engine: GameEngine):
    parts = callback.data.split(":")
    game_id = int(parts[1])
    ability_id = int(parts[2])

    alive = await game_engine.player_repo.get_alive_players(game_id)
    alive_data = []
    for p in alive:
        u = await game_engine.user_repo.get_by_id(p.user_id)
        alive_data.append({"user_id": p.user_id, "name": u.first_name if u else f"O'yinchi #{p.user_id}"})

    kb = get_ability_target_keyboard(game_id, ability_id, alive_data)
    await callback.message.edit_text(
        "🎯 <b>Qobiliyatni kimga ishlatmoqchisiz?</b>\nNishonni tanlang:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("use_ab_target:"))
async def handle_ability_target(callback: CallbackQuery, game_engine: GameEngine):
    parts = callback.data.split(":")
    game_id = int(parts[1])
    ability_id = int(parts[2])
    target_id = int(parts[3])

    res = await game_engine.use_ability(game_id, callback.from_user.id, ability_id, target_id)
    msg = res.get("message", "Qobiliyat ishlatildi.")
    
    await callback.answer(msg, show_alert=True)
    
    # Return to abilities list
    abilities = await game_engine.player_repo.get_player_abilities(game_id, callback.from_user.id)
    kb = get_player_abilities_keyboard(game_id, abilities)
    try:
        await callback.message.edit_text(
            f"⚡ <b>Qobiliyatlaringiz:</b>\n<i>{msg}</i>",
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception:
        pass
