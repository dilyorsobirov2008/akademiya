from aiogram import Router, types, F
from database.models import User, Course, CourseProgress
from sqlalchemy import select
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "🎓 Mening kurslarim")
async def show_my_courses(message: types.Message, session):
    stmt = select(Course).join(Course.progress).where(CourseProgress.user_id == message.from_user.id)
    result = await session.execute(stmt)
    courses = result.scalars().all()
    
    if not courses:
        await message.answer("Siz hali birorta kursga a'zo bo'lmabsiz.")
        return
        
    text = "🎓 **Sizning kurslaringiz:**\n\n"
    for course in courses:
        text += f"• {course.title}\n"
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📚 Bilimlar bazasi")
async def show_knowledge_base(message: types.Message):
    await message.answer(
        "📚 **Bilimlar bazasi**\n\n"
        "1. Kompaniya haqida\n"
        "2. Missiya va Qadriyatlar\n"
        "3. Lavozim yo'riqnomalari\n"
        "4. Xizmat standartlari\n\n"
        "Ko'rmoqchi bo'lgan bo'limni tanlang (Tez kunda...)",
        parse_mode="Markdown"
    )

@router.message(F.text == "🏆 Sertifikatlarim")
async def show_certificates(message: types.Message):
    await message.answer("📜 Sizda hali sertifikatlar mavjud emas. Kurslarni tugatib, testlardan o'ting!")

@router.message(F.text == "📈 Reytingim")
async def show_rating(message: types.Message):
    await message.answer("📈 **Umumiy Reyting (Top-10)**\n\nTez kunda real vaqt rejimida ko'rsatiladi!")

@router.message(F.text == "🗓 O'qitish rejam")
async def show_plan(message: types.Message, db_user: User):
    await message.answer(
        f"🗓 **Sizning o'qitish rejangiz ({db_user.role.value}):**\n\n"
        "1-hafta: Umumiy onboarding\n"
        "2-hafta: Professional modullar\n"
        "3-hafta: Amaliyot\n"
        "4-hafta: Sertifikatsiya"
    )

@router.message(F.text == "👨‍🏫 Mentor bilan aloqa")
async def contact_mentor(message: types.Message, db_user: User):
    if db_user.mentor_name:
        await message.answer(f"👨‍🏫 Sizning mentoringiz: **{db_user.mentor_name}**\n\nSavollaringizni shu yerda yozib qoldirishingiz mumkin.")
    else:
        await message.answer("Sizga hali mentor biriktirilmagan.")
