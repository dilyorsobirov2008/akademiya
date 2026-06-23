import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from bot.handlers.registration import router as registration_router
from bot.handlers.menu import router as menu_router
from bot.handlers.admin import router as admin_router
from bot.middlewares.db import DbSessionMiddleware
from database.connection import init_db, async_session
from bot.utils.scheduler import scheduler

load_dotenv()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Register Middlewares
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    
    # Global Error Handler
    @dp.error()
    async def global_error_handler(event: types.ErrorEvent):
        logging.error(f"Critical error: {event.exception}", exc_info=True)
        # You could notify admins here
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers
    dp.include_router(registration_router)
    dp.include_router(menu_router)
    dp.include_router(admin_router)
    
    # Set bot commands
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Botni qayta ishga tushirish"),
        types.BotCommand(command="help", description="Yordam va qo'llanma")
    ])
    
    # Start scheduler
    scheduler.start()
    
    # Check if we should use webhooks or polling
    webhook_url = os.getenv("WEBHOOK_URL")
    
    if webhook_url:
        # Webhook mode
        host = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("WEB_SERVER_PORT", 8080))
        
        await bot.set_webhook(url=webhook_url)
        
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        
        logging.info(f"Bot started on webhooks: {webhook_url}")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        # Keep the bot running
        await asyncio.Event().wait()
    else:
        # Polling mode (default)
        logging.info("Bot started on polling...")
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
