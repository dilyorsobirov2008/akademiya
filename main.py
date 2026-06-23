import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Called when bot starts — create DB tables."""
    from database.connection import init_db
    await init_db()
    logger.info("✅ Database initialized")


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.critical("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    # --- Middleware ---
    from database.connection import async_session
    from bot.middlewares.db import DbSessionMiddleware
    from bot.middlewares.user import UserMiddleware
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.update.middleware(UserMiddleware())

    # --- Global Error Handler ---
    @dp.error()
    async def global_error_handler(event: types.ErrorEvent):
        logger.error(f"Handler xatosi: {event.exception}", exc_info=True)

    # --- Register Routers ---
    from bot.handlers.registration import router as reg_router
    from bot.handlers.menu import router as menu_router
    from bot.handlers.admin import router as admin_router
    from bot.handlers.profile import router as profile_router
    from bot.handlers.tests import router as tests_router

    dp.include_router(reg_router)
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)
    dp.include_router(tests_router)

    # --- Bot Commands ---
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Botni ishga tushirish"),
        types.BotCommand(command="help", description="Yordam"),
        types.BotCommand(command="profile", description="Mening profilim"),
        types.BotCommand(command="admin", description="Admin panel"),
    ])

    # --- Startup actions ---
    dp.startup.register(on_startup)

    # --- Start scheduler ---
    from bot.utils.scheduler import scheduler
    scheduler.start()
    logger.info("✅ Scheduler started")

    # --- Webhook or Polling ---
    webhook_url = os.getenv("WEBHOOK_URL")
    logger.info(f"🔎 DEBUG: WEBHOOK_URL sozlanganmi? {'HA' if webhook_url else 'YOQ'}")
    if webhook_url:
        logger.info(f"🔎 DEBUG: WEBHOOK_URL qiymati: {webhook_url}")
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
        host = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("PORT", os.getenv("WEB_SERVER_PORT", "8080")))

        await bot.set_webhook(url=webhook_url)

        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        setup_application(app, dp, bot=bot)

        logger.info(f"🌐 Bot webhook rejimida ishga tushdi: {webhook_url} (port: {port})")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        await asyncio.Event().wait()
    else:
        logger.info("🤖 Bot polling rejimida ishga tushdi...")
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi!")
