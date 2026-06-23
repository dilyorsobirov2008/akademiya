from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from datetime import datetime, timedelta
import logging

scheduler = AsyncIOScheduler()
logger = logging.getLogger(__name__)

async def send_onboarding_reminder(bot: Bot, user_id: int, day: int):
    messages = {
        1: (
            "🌟 **1-kun: Onboarding boshlandi!**\n\n"
            "Bugun siz kompaniyamiz bilan tanishasiz:\n"
            "• Kompaniya haqida umumiy ma'lumot\n"
            "• Bizning missiyamiz va qadriyatlarimiz\n"
            "• Ichki tartib qoidalar\n"
            "• Kniga Novichka (PDF)\n\n"
            "📚 Ma'lumotlarni 'Bilimlar bazasi' bo'limidan topishingiz mumkin."
        ),
        3: (
            "📂 **3-kun: Bo'lim bilan tanishuv**\n\n"
            "Bugungi rejangiz:\n"
            "• Bo'lim tuzilishi\n"
            "• Lavozim yo'riqnomasi\n"
            "• Xizmat standartlari bilan tanishish"
        ),
        7: (
            "📝 **7-kun: Birinchi sinov**\n\n"
            "Bugun siz amaliy topshiriqlarni bajarasiz va birinchi testdan o'tasiz.\n"
            "Tayyor bo'lsangiz 'Testlar' bo'limiga kiring!"
        ),
        30: (
            "🏅 **30-kun: Yakuniy sertifikatsiya**\n\n"
            "Sizning adaptatsiya muddatingiz yakuniga yetdi.\n"
            "Bugun yakuniy sertifikatsiya testi va mentor baholashidan o'tasiz."
        )
    }
    
    if day in messages:
        try:
            await bot.send_message(user_id, messages[day], parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Reminder error Day {day} for {user_id}: {e}")

async def schedule_onboarding(bot: Bot, user_id: int):
    # Schedule for Day 1, 3, 7, 30
    days = [1, 3, 7, 30]
    for day in days:
        run_date = datetime.now() + timedelta(days=day-1 if day > 1 else 0, minutes=1) # Simplified for testing: Day 1 is immediate
        scheduler.add_job(
            send_onboarding_reminder,
            'date',
            run_date=run_date,
            args=[bot, user_id, day],
            id=f"onboarding_{user_id}_{day}"
        )
