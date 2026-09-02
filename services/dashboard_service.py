"""
Dashboard service for managing group chat message updates.
"""
from aiogram import Bot
from game.engine import GameEngine
from utils.formatters import format_dashboard
from bot.keyboards.game_kb import get_game_dashboard_keyboard


class DashboardService:
    def __init__(self, bot: Bot, game_engine: GameEngine):
        self.bot = bot
        self.game_engine = game_engine

    async def refresh_dashboard(self, game_id: int) -> bool:
        """Refreshes the pinned message in group chat."""
        d_data = await self.game_engine.get_game_dashboard_data(game_id)
        if not d_data:
            return False

        game = d_data["game"]
        if not game.dashboard_message_id:
            return False

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
            await self.bot.edit_message_text(
                chat_id=game.group_chat_id,
                message_id=game.dashboard_message_id,
                text=text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return True
        except Exception:
            return False
