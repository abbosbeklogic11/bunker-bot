"""
Group admin commands for BUNKER game.
"""
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from bot.filters import IsGroupChat, IsAdmin
from game.engine import GameEngine
from bot.keyboards.admin_kb import get_admin_menu_keyboard
from models.user import UserModel

router = Router()


@router.message(Command("admin"), IsGroupChat(), IsAdmin())
async def cmd_group_admin(message: Message):
    kb = get_admin_menu_keyboard()
    await message.reply("⚙️ <b>BUNKER ADMIN BOSHQARUV PANELI:</b>", reply_markup=kb, parse_mode="HTML")


@router.message(Command("stop_game"), IsGroupChat())
async def cmd_stop_game(message: Message, game_engine: GameEngine, user: UserModel, bot: Bot):
    game = await game_engine.game_repo.get_active_game_by_group(message.chat.id)
    if not game:
        await message.reply("❌ Guruhda faol o'yin topilmadi.")
        return

    # Check permission
    is_allowed = (game.created_by == user.id) or user.is_admin
    if not is_allowed:
        try:
            member = await bot.get_chat_member(message.chat.id, user.id)
            if member.status in ("creator", "administrator"):
                is_allowed = True
        except Exception:
            pass

    if not is_allowed:
        await message.reply("❌ Faqat o'yin yaratuvchisi yoki guruh admini o'yinni to'xtata oladi!")
        return

    await game_engine.game_repo.finish_game(game.id)
    await game_engine.timer_engine.cancel_timer(game.id)
    await message.reply(
        f"⏹ <b>Bunker o'yini #{game.id} to'xtatildi.</b>\n"
        f"Yangi o'yin boshlash uchun /bunker yuboring.",
        parse_mode="HTML"
    )
