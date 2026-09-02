"""
Notification service module for BUNKER game.
Subscribes to all Game Engine EventBus events and dispatches messages to Telegram groups and private user chats.
Controls group chat permissions (muting chat during voting).
"""
from typing import Dict, Any, List
import asyncio
import logging
from aiogram import Bot
from aiogram.types import ChatPermissions
from game.engine_events import EventBus, GameEvent, GameEventType
from game.engine import GameEngine
from utils.formatters import (
    format_dashboard, format_private_cards, format_elimination_message,
    format_duel_message, format_event_message, format_game_over
)
from bot.keyboards.game_kb import get_game_dashboard_keyboard
from bot.keyboards.ability_kb import get_player_abilities_keyboard, get_player_cards_keyboard
from bot.keyboards.voting_kb import get_voting_keyboard, get_duel_voting_keyboard
from bot.keyboards.reveal_kb import get_reveal_attribute_keyboard, ATTR_NAMES
from game.data.apocalypse import get_apocalypse_by_type

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, bot: Bot, game_engine: GameEngine):
        self.bot = bot
        self.game_engine = game_engine

    def register_subscribers(self, event_bus: EventBus) -> None:
        """Subscribes handlers to all game events."""
        event_bus.subscribe(GameEventType.GAME_STARTED, self.on_game_started)
        event_bus.subscribe(GameEventType.CARDS_DISTRIBUTED, self.on_cards_distributed)
        event_bus.subscribe(GameEventType.ATTRIBUTE_REVEALED, self.on_attribute_revealed)
        event_bus.subscribe(GameEventType.PLAYER_ATTRIBUTE_REVEALED, self.on_player_attribute_revealed)
        event_bus.subscribe(GameEventType.PHASE_CHANGED, self.on_phase_changed)
        event_bus.subscribe(GameEventType.PLAYER_ELIMINATED, self.on_player_eliminated)
        event_bus.subscribe(GameEventType.DUEL_STARTED, self.on_duel_started)
        event_bus.subscribe(GameEventType.EVENT_TRIGGERED, self.on_event_triggered)
        event_bus.subscribe(GameEventType.WINNER_DETERMINED, self.on_winner_determined)
        event_bus.subscribe(GameEventType.VOTE_SUBMITTED, self.on_vote_submitted)

    _voting_messages: dict = {}

    async def _mute_chat(self, chat_id: int) -> None:
        """Mutes group chat during voting phase."""
        try:
            await self.bot.set_chat_permissions(
                chat_id=chat_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
        except Exception as e:
            logger.debug(f"Could not mute chat {chat_id}: {e}")

    async def _unmute_chat(self, chat_id: int) -> None:
        """Unmutes group chat after voting concludes."""
        try:
            await self.bot.set_chat_permissions(
                chat_id=chat_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
        except Exception as e:
            logger.debug(f"Could not unmute chat {chat_id}: {e}")

    async def _update_group_dashboard(self, game_id: int) -> None:
        """Fetches fresh game data and updates the pinned group dashboard."""
        d_data = await self.game_engine.get_game_dashboard_data(game_id)
        if not d_data:
            return

        game = d_data["game"]
        if not game.dashboard_message_id:
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
            await self.bot.edit_message_text(
                chat_id=game.group_chat_id,
                message_id=game.dashboard_message_id,
                text=text,
                reply_markup=kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.debug(f"Error updating dashboard: {e}")

    async def on_game_started(self, event: GameEvent) -> None:
        game_id = event.game_id
        data = event.data
        ap = data.get("apocalypse", {})
        
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        announcement = (
            f"🚀 <b>BUNKER O'YINI BOSHLANDI!</b>\n\n"
            f"{ap.get('emoji', '☢️')} <b>Apokalipsis:</b> {ap.get('name')}\n"
            f"📜 <i>{ap.get('description')}</i>\n\n"
            f"🤫 <i>Barcha o'yinchilarga maxfiy kartalar shaxsiy chatga yuborilmoqda!</i>"
        )
        try:
            sent = await self.bot.send_message(game.group_chat_id, announcement, parse_mode="HTML")
            await self.bot.pin_chat_message(chat_id=game.group_chat_id, message_id=sent.message_id, disable_notification=True)
        except Exception as e:
            logger.error(f"Error sending game start announcement: {e}")

    async def on_cards_distributed(self, event: GameEvent) -> None:
        game_id = event.game_id
        player_ids = event.data.get("player_ids", [])

        for uid in player_ids:
            try:
                p_data = await self.game_engine.get_player_private_data(game_id, uid)
                if not p_data:
                    continue

                text = format_private_cards(game_id, p_data)
                
                # Send private cards message
                await self.bot.send_message(chat_id=uid, text=text, parse_mode="HTML")
                
                # Send quick action buttons
                kb_ab = get_player_abilities_keyboard(game_id, p_data.get("abilities", []))
                await self.bot.send_message(
                    chat_id=uid,
                    text="⚡ <b>Qobiliyatlaringiz:</b>",
                    reply_markup=kb_ab,
                    parse_mode="HTML"
                )
                
                kb_cd = get_player_cards_keyboard(game_id, p_data.get("cards", []))
                await self.bot.send_message(
                    chat_id=uid,
                    text="🃏 <b>Maxfiy kartalaringiz:</b>",
                    reply_markup=kb_cd,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Could not send private cards to user {uid}: {e}")

    async def on_attribute_revealed(self, event: GameEvent) -> None:
        game_id = event.game_id
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        # Mute group chat during attribute selection so players focus on buttons
        await self._mute_chat(game.group_chat_id)

        duration = event.data.get("duration", 90)
        time_text = "1.5 daqiqa (90 sek)" if duration == 90 else f"{duration} sek"
        kb = get_reveal_attribute_keyboard(game_id)
        msg = (
            f"🔔 <b>{game.current_round}-RAUND: XUSUSIYAT OCHISH! (⏱ {time_text})</b>\n\n"
            f"🤫 <i>O'yinchilar xususiyatini tanlab olishi uchun chat vaqtincha yopildi.</i>\n\n"
            f"🎯 <b>Har bir o'yinchi {time_text} ichida o'zining 1 ta xususiyatini tanlab ochishi kerak!</b>\n"
            f"<i>(Hamma ochib bo'lgach yoki {time_text} tugagach, 2 daqiqalik muhokama boshlanadi va chat ochiladi)</i>\n\n"
            f"Qaysi xususiyatingizni ochmoqchisiz? Quyidagi tugmalardan birini bosing:"
        )
        try:
            await self.bot.send_message(game.group_chat_id, msg, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass

        await self._update_group_dashboard(game_id)

    async def on_player_attribute_revealed(self, event: GameEvent) -> None:
        game_id = event.game_id
        data = event.data
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        user_name = data.get("user_name", "O'yinchi")
        attr_type = data.get("attribute_type", "")
        attr_val = data.get("attribute_value", "")

        attr_label = ATTR_NAMES.get(attr_type, attr_type.title())

        msg = (
            f"📢 <b>{user_name}</b> o'zining <b>{attr_label}</b>ini ochdi:\n"
            f"👉 <b>{attr_val}</b>"
        )
        try:
            await self.bot.send_message(game.group_chat_id, msg, parse_mode="HTML")
        except Exception:
            pass

        await self._update_group_dashboard(game_id)

    async def on_phase_changed(self, event: GameEvent) -> None:
        game_id = event.game_id
        phase = event.data.get("phase")
        round_num = event.data.get("round", 1)
        duration = event.data.get("duration", 60)

        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        if phase == "DISCUSSION":
            # Ensure chat is unmuted
            await self._unmute_chat(game.group_chat_id)
            mins = max(1, duration // 60)
            msg = (
                f"🗣 <b>{round_num}-RAUND MUHOKAMASI BOSHLANDI! (⏱ {mins} daqiqa)</b>\n\n"
                f"💬 <b>Chat ochildi!</b> Guruhda faol bahslashib, o'zingizni himoya qiling va nomzodlarni muhokama qiling!\n"
                f"<i>⏱ {mins} daqiqadan so'ng Ovoz berish bosqichi boshlanadi.</i>"
            )
            try:
                await self.bot.send_message(game.group_chat_id, msg, parse_mode="HTML")
            except Exception:
                pass

        elif phase == "ABILITY_PHASE":
            bot_info = await self.bot.get_me()
            msg = (
                f"⚡ <b>QOBILIYATLAR BOSQICHI! (⏱ {duration} sek)</b>\n\n"
                f"O'yinchilar @{bot_info.username} shaxsiy chatiga o'tib, o'z maxsus qobiliyatlarini ishlatishlari mumkin!\n"
                f"<i>(Shifokor, Detektiv, Bloker va h.k.)</i>"
            )
            try:
                await self.bot.send_message(game.group_chat_id, msg, parse_mode="HTML")
            except Exception:
                pass

        elif phase in ("VOTING", "DUEL"):
            # Mute chat during voting
            await self._mute_chat(game.group_chat_id)

            alive_players = await self.game_engine.player_repo.get_alive_players(game_id)
            alive_data = []
            for p in alive_players:
                u = await self.game_engine.user_repo.get_by_id(p.user_id)
                alive_data.append({"user_id": p.user_id, "name": u.first_name if u else f"O'yinchi #{p.user_id}"})

            kb = get_voting_keyboard(game_id, alive_data, voter_id=0)
            msg = (
                f"🗳 <b>OVOZ BERISH BOSQICHI BOSHLANDI! (⏱ {duration} sek)</b>\n\n"
                f"🤫 <i>Ovoz berish vaqtida guruh chati vaqtincha yopildi (ovoz tugagach ochiladi).</i>\n\n"
                f"Kimni bunkerdan chiqarib yuboramiz?\n"
                f"<i>O'zingiz nomzod deb bilgan o'yinchining tugmasini bosing:</i>"
            )
            try:
                sent = await self.bot.send_message(game.group_chat_id, msg, reply_markup=kb, parse_mode="HTML")
                self._voting_messages[game_id] = sent.message_id
            except Exception:
                pass

        elif phase == "NO_VOTES":
            await self._unmute_chat(game.group_chat_id)
            msg = (
                f"⚠️ <b>OVOZ BERISHDA HECH KIM OVOZ BERMADI!</b>\n\n"
                f"Bunkerdan hech kim chiqarilmadi.\n"
                f"O'yin shu tarkib bilan keyingi raundga o'tadi!"
            )
            try:
                await self.bot.send_message(game.group_chat_id, msg, parse_mode="HTML")
            except Exception:
                pass

        await self._update_group_dashboard(game_id)

    async def on_vote_submitted(self, event: GameEvent) -> None:
        """Dynamically updates the group voting message with live vote counts."""
        game_id = event.game_id
        data = event.data
        vote_counts = data.get("vote_counts", {})
        voted_count = data.get("voted_count", 0)
        alive_count = data.get("alive_count", 0)

        msg_id = self._voting_messages.get(game_id)
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game or not msg_id:
            return

        alive_players = await self.game_engine.player_repo.get_alive_players(game_id)
        alive_data = []
        for p in alive_players:
            u = await self.game_engine.user_repo.get_by_id(p.user_id)
            alive_data.append({"user_id": p.user_id, "name": u.first_name if u else f"O'yinchi #{p.user_id}"})

        kb = get_voting_keyboard(game_id, alive_data, voter_id=0, votes_tally=vote_counts)
        msg = (
            f"🗳 <b>OVOZ BERISH JARAYONI: ({voted_count}/{alive_count} ovoz berildi)</b>\n\n"
            f"🤫 <i>Ovoz berish vaqtida guruh chati vaqtincha yopildi.</i>\n\n"
            f"Kimni bunkerdan chiqarib yuboramiz?\n"
            f"<i>O'zingiz nomzod deb bilgan o'yinchining tugmasini bosing:</i>"
        )
        try:
            await self.bot.edit_message_text(
                chat_id=game.group_chat_id,
                message_id=msg_id,
                text=msg,
                reply_markup=kb,
                parse_mode="HTML"
            )
        except Exception:
            pass

    async def on_player_eliminated(self, event: GameEvent) -> None:
        game_id = event.game_id
        data = event.data
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        # Unmute chat after voting concludes
        await self._unmute_chat(game.group_chat_id)

        if data.get("saved_by_protection"):
            uid = data.get("user_id")
            u = await self.game_engine.user_repo.get_by_id(uid)
            name = u.first_name if u else f"O'yinchi #{uid}"
            msg = f"🛡️ <b>{name}</b> himoya qalqoni tufayli chiqarilishdan saqlanib qoldi!"
            try:
                await self.bot.send_message(game.group_chat_id, msg, parse_mode="HTML")
            except Exception:
                pass
            return

        uid = data.get("user_id")
        u = await self.game_engine.user_repo.get_by_id(uid)
        name = u.first_name if u else f"O'yinchi #{uid}"
        votes = data.get("votes", 0)
        alive = data.get("alive_count", 0)

        text = format_elimination_message(name, votes, alive)
        try:
            await self.bot.send_message(game.group_chat_id, text, parse_mode="HTML")
            await self.bot.send_message(
                chat_id=uid,
                text="💀 <b>Afsuski, siz ovoz berish natijasida bunkerdan chiqarildingiz!</b>\nKeyingi o'yinlarda omad!",
                parse_mode="HTML"
            )
        except Exception:
            pass

        await self._update_group_dashboard(game_id)

    async def on_duel_started(self, event: GameEvent) -> None:
        game_id = event.game_id
        data = event.data
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        tied_ids = data.get("tied_user_ids", [])
        candidates = []
        for uid in tied_ids:
            u = await self.game_engine.user_repo.get_by_id(uid)
            candidates.append({"user_id": uid, "name": u.first_name if u else f"O'yinchi #{uid}"})

        candidate_names = [c["name"] for c in candidates]
        text = format_duel_message(candidate_names, data.get("duration", 60))
        kb = get_duel_voting_keyboard(game_id, candidates, voter_id=0)

        try:
            await self.bot.send_message(game.group_chat_id, text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass

        await self._update_group_dashboard(game_id)

    async def on_event_triggered(self, event: GameEvent) -> None:
        game_id = event.game_id
        data = event.data
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        text = format_event_message(
            event=data.get("event", {}),
            resolved=data.get("resolved", False),
            resolvers=data.get("resolvers", []),
            consequences=data.get("consequences", {})
        )
        try:
            await self.bot.send_message(game.group_chat_id, text, parse_mode="HTML")
        except Exception:
            pass

    async def on_winner_determined(self, event: GameEvent) -> None:
        game_id = event.game_id
        data = event.data
        game = await self.game_engine.game_repo.get_by_id(game_id)
        if not game:
            return

        # Unmute chat
        await self._unmute_chat(game.group_chat_id)

        winners = data.get("winners", [])
        rewards = data.get("rewards", [])
        all_players = await self.game_engine.player_repo.get_all_players(game_id)
        
        ap = get_apocalypse_by_type(game.apocalypse_type or "nuclear")
        evaluation = data.get("evaluation")
        text = format_game_over(winners, ap, total_started=len(all_players), evaluation=evaluation)
        
        try:
            await self.bot.send_message(game.group_chat_id, text, parse_mode="HTML")
        except Exception:
            pass

        # Send private reward notifications
        for rew in rewards:
            uid = rew["user_id"]
            place = rew.get("place")
            coins = rew.get("coins", 0)
            diamonds = rew.get("diamonds", 0)
            bonus = rew.get("bonus_type")

            if place:
                p_msg = (
                    f"🏆 <b>TABRIKLAYMIZ!</b>\n\n"
                    f"Siz BUNKER o'yinida <b>{place}-o'rinni</b> egallab omon qoldingiz!\n\n"
                    f"🎁 <b>Mukofotingiz:</b>\n"
                    f"🪙 +{coins:,} Coins\n"
                    f"💎 +{diamonds} Diamonds"
                )
            else:
                p_msg = (
                    f"🌟 <b>MAXSUS MUKOFOT!</b> ({bonus})\n\n"
                    f"🎁 +{coins:,} Coins, +{diamonds} Diamonds hisobingizga qo'shildi!"
                )
            
            try:
                await self.bot.send_message(chat_id=uid, text=p_msg, parse_mode="HTML")
            except Exception:
                pass
