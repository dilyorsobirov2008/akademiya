from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from datetime import datetime, timedelta
import logging

scheduler = AsyncIOScheduler()

async def send_onboarding_reminder(bot: Bot, user_id: int, day: int):
    messages = {
        1: "🌟 **Xush kelibsiz!** Bugun sizning 1-kuningiz.\n\n"
           "Kompaniya haqida, missiyamiz va qadriyatlarimiz bilan tanishib chiqing.\n"
           "📚 **Bilimlar bazasi** -> **Onboarding** bo'limiga kiring.",
        3: "📅 **3-bugun!**\n\n"
           "Bugun bo'limingiz bilan tanishuv va xizmat standartlarini o'rganish vaqti keldi.\n"
           "Lavozim yo'riqnomasi sizni kutmoqda!",
        7: "🚀 **1 hafta o'tdi!**\n\n"
           "Birinchi amaliy topshiriqlarni bajarish va test topshirish vaqti keldi.",
        30: "🎓 **30 kun!**\n\n"
            "Yakuniy sertifikatsiya vaqtiga yetib keldik. Omad tilaymiz!"
    }
    
    text = messages.get(day, "O'qitish eslatmasi!")
    try:
        await bot.send_message(user_id, text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Failed to send reminder to {user_id}: {e}")

def schedule_onboarding(bot: Bot, user_id: int):
    # Schedule for Day 1 (immediate or later), Day 3, 7, 30
    now = datetime.now()
    
    # Day 1
    scheduler.add_job(send_onboarding_reminder, 'date', run_date=now + timedelta(minutes=1), args=[bot, user_id, 1])
    # Day 3
    scheduler.add_job(send_onboarding_reminder, 'date', run_date=now + timedelta(days=3), args=[bot, user_id, 3])
    # Day 7
    scheduler.add_job(send_onboarding_reminder, 'date', run_date=now + timedelta(days=7), args=[bot, user_id, 7])
    # Day 30
    scheduler.add_job(send_onboarding_reminder, 'date', run_date=now + timedelta(days=30), args=[bot, user_id, 30])
