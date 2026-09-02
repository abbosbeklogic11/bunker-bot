"""
Voting callbacks handler for BUNKER game.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from game.engine import GameEngine

router = Router()


@router.callback_query(F.data.startswith("vote:"))
async def handle_vote_submission(callback: CallbackQuery, game_engine: GameEngine):
    parts = callback.data.split(":")
    game_id = int(parts[1])
    target_id = int(parts[2])
    voter_id = callback.from_user.id

    res = await game_engine.submit_vote(game_id, voter_id, target_id)
    if not res.get("success"):
        err = res.get("error")
        if err == "NOT_IN_VOTING":
            await callback.answer("❌ Ovoz berish bosqichi yakunlangan!", show_alert=True)
        elif err == "ALREADY_VOTED":
            await callback.answer("❌ Siz allaqachon ovoz bergansiz!", show_alert=True)
        elif err == "CANNOT_VOTE_SELF":
            await callback.answer("❌ O'zingizga ovoz bera olmaysiz!", show_alert=True)
        elif err in ("VOTER_NOT_ALIVE", "TARGET_NOT_ALIVE"):
            await callback.answer("❌ Bu o'yinchi tirik emas!", show_alert=True)
        else:
            await callback.answer("❌ Ovoz berishda xatolik.", show_alert=True)
        return

    voted_count = res.get("voted_count", 0)
    alive_count = res.get("alive_count", 0)

    await callback.answer(
        f"✅ Ovozingiz qabul qilindi! ({voted_count}/{alive_count} ta ovoz berildi)",
        show_alert=True
    )
