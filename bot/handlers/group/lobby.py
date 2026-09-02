"""
Group lobby commands handler for BUNKER game.
"""
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from bot.filters import IsGroupChat
from game.engine import GameEngine
from utils.formatters import format_lobby_message
from bot.keyboards.lobby_kb import get_lobby_keyboard
from models.user import UserModel

router = Router()


@router.message(Command("bunker"), IsGroupChat())
async def cmd_bunker(message: Message, game_engine: GameEngine, user: UserModel, bot: Bot):
    """Starts a new Bunker lobby in the group."""
    res = await game_engine.create_game(group_chat_id=message.chat.id, created_by=user.id)
    
    if not res.get("success"):
        err = res.get("error")
        if err == "ALREADY_ACTIVE_GAME":
            await message.reply("⚠️ Bu guruhda allaqachon faol o'yin mavjud! To'xtatish uchun /stop_game buyrug'ini yuboring.")
        else:
            await message.reply("❌ O'yin yaratishda xatolik yuz berdi.")
        return

    game = res.get("game")
    
    players_data = [{"name": user.first_name, "first_name": user.first_name}]
    text = format_lobby_message(game.id, players_data, max_players=game_engine.config.MAX_PLAYERS, min_players=game_engine.config.MIN_PLAYERS)
    kb = get_lobby_keyboard(game.id, player_count=1, max_players=game_engine.config.MAX_PLAYERS, is_creator=True)

    sent_msg = await message.answer(text, reply_markup=kb, parse_mode="HTML")
    await game_engine.game_repo.update_dashboard_message_id(game.id, sent_msg.message_id)

    # Automatically pin the game lobby message
    try:
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=sent_msg.message_id, disable_notification=True)
    except Exception:
        pass


@router.message(Command("start_game"), IsGroupChat())
async def cmd_start_game(message: Message, game_engine: GameEngine, user: UserModel):
    """Admin or creator force start command."""
    game = await game_engine.game_repo.get_active_game_by_group(message.chat.id)
    if not game:
        await message.reply("❌ Guruhda faol o'yin lobby'si topilmadi.")
        return

    if game.created_by != user.id and not user.is_admin:
        await message.reply("❌ Faqat o'yin yaratuvchisi yoki admin o'yinni boshlashi mumkin!")
        return

    res = await game_engine.start_game(game.id, by_user_id=user.id)
    if not res.get("success"):
        await message.reply(f"❌ O'yin boshlanmadi: {res.get('error')}")
