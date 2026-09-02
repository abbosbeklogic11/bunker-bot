"""
BUNKER — Telegram Multiplayer Game Platform
Application Entry Point (aiogram 3.x + SQLite / Postgres + In-Memory / Redis + APScheduler)
"""
import asyncio
import os
import sys
import logging

try:
    from loguru import logger
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    logger = logging.getLogger("bunker_bot")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config.settings import settings
from bot.config.game_config import default_game_config
from database.connection import create_pool, close_pool
from database.repositories import (
    UserRepository, GameRepository, PlayerRepository,
    VoteRepository, EventRepository, AchievementRepository, ChannelRepository
)
from game.engine_events import EventBus
from game.timers.timer_engine import TimerEngine
from game.timers.scheduler import GameScheduler
from game.engine import GameEngine
from services.notification_service import NotificationService
from services.dashboard_service import DashboardService

# Middlewares
from bot.middlewares import AuthMiddleware, ThrottlingMiddleware

# Handlers & Callbacks
from bot.handlers import group_lobby_router, group_admin_router, private_start_router, private_admin_router
from bot.callbacks import (
    lobby_cb_router, game_cb_router, voting_cb_router,
    ability_cb_router, card_cb_router
)


async def main():
    if hasattr(logger, "remove") and hasattr(logger, "add"):
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL
        )

    logger.info("Starting BUNKER Game Server...")

    if not settings.BOT_TOKEN or "TOKEN" in settings.BOT_TOKEN:
        logger.error("❌ XATOLIK: .env faylida BOT_TOKEN ko'rsatilmagan!")
        logger.error("Iltimos, .env faylini oching va @BotFather bergan tokeningizni kiriting.")
        return

    # 1. Database connection pool (Postgres with automatic SQLite bunker.db fallback)
    pool = await create_pool()

    # 2. Redis connection (with automatic in-memory fallback)
    redis_client = None
    if settings.REDIS_URL:
        try:
            import redis.asyncio as redis
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            await asyncio.wait_for(r.ping(), timeout=2.0)
            redis_client = r
            logger.info("Connected to Redis server!")
        except Exception:
            logger.info("Redis server not found. Using fast In-Memory Timer Engine.")
            redis_client = None

    # 3. Repositories
    user_repo = UserRepository(pool)
    game_repo = GameRepository(pool)
    player_repo = PlayerRepository(pool)
    vote_repo = VoteRepository(pool)
    event_repo = EventRepository(pool)
    achievement_repo = AchievementRepository(pool)
    channel_repo = ChannelRepository(pool)

    # 4. Timer & Event Systems
    timer_engine = TimerEngine(redis_client)
    event_bus = EventBus()

    # 5. Core Game Engine
    game_engine = GameEngine(
        game_repo=game_repo,
        player_repo=player_repo,
        vote_repo=vote_repo,
        event_repo=event_repo,
        user_repo=user_repo,
        achievement_repo=achievement_repo,
        timer_engine=timer_engine,
        event_bus=event_bus,
        config=default_game_config
    )

    # 6. Bot and Dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # 7. Services
    notif_service = NotificationService(bot=bot, game_engine=game_engine)
    notif_service.register_subscribers(event_bus)
    dash_service = DashboardService(bot=bot, game_engine=game_engine)

    # 8. Scheduler
    scheduler = GameScheduler(timer_engine=timer_engine, game_engine=game_engine)
    await scheduler.start()

    # 9. Register Global Middlewares
    dp.update.middleware(AuthMiddleware(user_repo=user_repo))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit_sec=0.4))

    # 10. Register Dependency Injection in Dispatcher
    dp["game_engine"] = game_engine
    dp["user_repo"] = user_repo
    dp["game_repo"] = game_repo
    dp["player_repo"] = player_repo
    dp["vote_repo"] = vote_repo
    dp["event_repo"] = event_repo
    dp["achievement_repo"] = achievement_repo
    dp["channel_repo"] = channel_repo
    dp["dashboard_service"] = dash_service

    # 11. Register Routers
    dp.include_router(private_admin_router)
    dp.include_router(private_start_router)
    dp.include_router(group_lobby_router)
    dp.include_router(group_admin_router)
    dp.include_router(lobby_cb_router)
    dp.include_router(game_cb_router)
    dp.include_router(voting_cb_router)
    dp.include_router(ability_cb_router)
    dp.include_router(card_cb_router)

    # 12. Startup tasks: recover active games
    try:
        active_games = await game_repo.get_active_games()
        logger.info(f"Loaded {len(active_games)} active game sessions from database.")
    except Exception as e:
        logger.warning(f"Could not load active games: {e}")

    # Optional HTTP health server for cloud platforms (Render/Railway Web Service)
    port = int(os.getenv("PORT", 0))
    runner = None
    if port > 0:
        try:
            from aiohttp import web
            async def handle_health(request):
                return web.Response(text="BUNKER Telegram Bot is Running Live!")
            app = web.Application()
            app.router.add_get("/", handle_health)
            app.router.add_get("/health", handle_health)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            logger.info(f"🌐 Cloud Health Check server listening on port {port}")
        except Exception as e:
            logger.warning(f"Could not start health check web server: {e}")

    logger.info("🤖 BUNKER Telegram Bot is now polling for updates!")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Shutting down BUNKER Game Server...")
        if runner:
            await runner.cleanup()
        await scheduler.stop()
        if redis_client:
            await redis_client.aclose()
        await close_pool()
        await bot.session.close()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
