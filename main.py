import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.handlers.registration import router as registration_router
from bot.handlers.menu import router as menu_router
from database.connection import init_db
from bot.utils.scheduler import scheduler

load_dotenv()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Initialize DB
    # await init_db() # Uncomment this when DB URL is valid
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers
    dp.include_router(registration_router)
    dp.include_router(menu_router)
    
    # Start scheduler
    scheduler.start()
    
    # Start polling
    logging.info("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
