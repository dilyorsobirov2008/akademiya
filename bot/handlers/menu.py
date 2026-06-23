from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from database.models import User, Course, CourseProgress, TestResult
from sqlalchemy import select
from bot.keyboards.reply import get_main_menu
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "🎓 Mening kurslarim")
async def show_my_courses(message: types.Message, session):
    try:
        # Check courses
        stmt = select(Course).join(CourseProgress).where(CourseProgress.user_id == message.from_user.id)
        result = await session.execute(stmt)
        courses = result.scalars().all()
        
        if not courses:
            await message.answer("🎓 **Hozirda sizda faol kurslar yo'q.**\n\nMentor tomonidan biriktirilishi kutilmoqda.", parse_mode="Markdown")
            return
            
        text = "🎓 **Sizning kurslaringiz:**\n\n"
        for course in courses:
            text += f"• {course.title}\n"
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in show_my_courses: {e}")
        await message.answer("❌ Ma'lumotlarni yuklashda xatolik yuz berdi.")

@router.message(F.text == "📚 Bilimlar bazasi")
async def show_knowledge_base(message: types.Message):
    await message.answer(
        "📚 **Bilimlar bazasi**\n\n"
        "• Kompaniya haqida\n"
        "• Missiya va Qadriyatlar\n"
        "• Lavozim yo'riqnomalari\n"
        "• Xizmat standartlari\n\n"
        "Ushbu bo'lim tez kunda PDF materiallar bilan to'ldiriladi.",
        parse_mode="Markdown"
    )

@router.message(F.text == "📝 Testlar")
async def redirect_to_tests(message: types.Message):
    await message.answer("📝 Testlar ro'yxatini ko'rish uchun menyudagi 'Testlar' tugmasini kiriting (yoki /tests xabarini yozing).")

@router.message(F.text == "🏆 Sertifikatlarim")
async def show_certificates(message: types.Message):
    await message.answer("📜 Sizda hali sertifikatlar mavjud emas. Kurslarni tugatib, testlardan o'ting!")

@router.message(F.text == "📈 Reytingim")
async def show_rating(message: types.Message):
    await message.answer("📈 **Umumiy Reyting (Top-10)**\n\nSizning o'riningiz: **Top 20%** ichida.\nHisoblash davom etmoqda...", parse_mode="Markdown")

@router.message(F.text == "🗓 O'qitish rejam")
async def show_plan(message: types.Message, db_user: User):
    await message.answer(
        f"🗓 **Sizning o'qitish rejangiz ({db_user.role.value.upper()}):**\n\n"
        "• 1-hafta: Onboarding\n"
        "• 2-hafta: Sotuv standartlari\n"
        "• 3-hafta: Kassa intizomi\n"
        "• 4-hafta: Yakuniy sertifikatsiya",
        parse_mode="Markdown"
    )

@router.message(F.text == "👨‍🏫 Mentor bilan aloqa")
async def contact_mentor(message: types.Message, db_user: User):
    if db_user and db_user.mentor_name:
        await message.answer(f"👨‍🏫 Sizning mentoringiz: **{db_user.mentor_name}**\n\nSavollaringizni yozib qoldirishingiz mumkin.")
    else:
        await message.answer("Sizga hali mentor biriktirilmagan.")

@router.message(F.text == "💬 Savol berish")
async def ask_question(message: types.Message):
    await message.answer(
        "💬 **Akademiya ma'muriyatiga savol berish**\n\n"
        "Savolingizni bir guruh mutaxassislar ko'rib chiqadi. Iltimos, savolingizni yozing:",
        parse_mode="Markdown"
    )

@router.message(F.text == "📋 Baholash natijalari")
async def show_results(message: types.Message, session):
    stmt = select(TestResult).where(TestResult.user_id == message.from_user.id)
    result = await session.execute(stmt)
    results = result.scalars().all()
    
    if not results:
        await message.answer("Sizda hali baholash natijalari mavjud emas.")
    else:
        await message.answer(f"Sizda {len(results)} ta test natijasi bor.")

@router.message(F.text == "🏅 Karyera yo'li")
async def show_career_path(message: types.Message, db_user: User):
    await message.answer(
        "🏅 **Karyera yo'li (T.Z.):**\n\n"
        "Sotuvchi ➡️ Katta sotuvchi ➡️ Supervayzer ➡️ Filial rahbari\n\n"
        f"Sizning hozirgi holatingiz: **{db_user.position}**\n"
        "Keyingi bosqich uchun 2 ta kurs va 1 ta test topshirishingiz kerak.",
        parse_mode="Markdown"
    )
