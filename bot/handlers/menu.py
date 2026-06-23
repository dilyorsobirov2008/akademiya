from aiogram import Router, types, F
from aiogram.filters import Command
from bot.keyboards.main_menu import get_main_menu
from database.models import User, CourseProgress, TestResult, Certificate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

router = Router()
logger = logging.getLogger(__name__)


# ==================== Mening kurslarim ====================
@router.message(F.text == "🎓 Mening kurslarim")
async def my_courses(message: types.Message, session: AsyncSession):
    stmt = select(CourseProgress).where(CourseProgress.user_id == message.from_user.id)
    result = await session.execute(stmt)
    progress_list = result.scalars().all()

    if not progress_list:
        await message.answer(
            "📚 **Sizga hali kurs tayinlanmagan.**\n\n"
            "Onboarding kurslaringiz tez orada ochiladi.\n"
            "Iltimos, mentoringiz bilan bog'laning.",
            parse_mode="Markdown"
        )
        return

    text = "📚 **Sizning faol kurslaringiz:**\n\n"
    for i, p in enumerate(progress_list, 1):
        pct = int((p.completed_lessons / p.total_lessons * 100)) if p.total_lessons > 0 else 0
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        text += f"{i}. Kurs #{p.course_id}\n   {bar} {pct}%\n\n"

    await message.answer(text, parse_mode="Markdown")


# ==================== Bilimlar bazasi ====================
@router.message(F.text == "📚 Bilimlar bazasi")
async def knowledge_base(message: types.Message):
    await message.answer(
        "📖 **Bilimlar bazasi**\n\n"
        "Kerakli bo'limni tanlang:\n\n"
        "📁 **Umumiy kurslar**\n"
        "   • Kompaniya haqida\n"
        "   • Korporativ madaniyat\n"
        "   • Mehnat xavfsizligi\n\n"
        "📁 **Sotuv akademiyasi**\n"
        "   • Sotuv bosqichlari\n"
        "   • SPIN texnikasi\n"
        "   • Cross-sell / Up-sell\n\n"
        "📁 **Kassir akademiyasi**\n"
        "   • Kassa intizomi\n"
        "   • Pul bilan ishlash\n\n"
        "📁 **Ombor akademiyasi**\n"
        "   • FIFO tamoyili\n"
        "   • Inventarizatsiya\n\n"
        "📁 **Liderlik akademiyasi**\n"
        "   • KPI va Coaching\n"
        "   • Delegatsiya va Feedback",
        parse_mode="Markdown"
    )


# ==================== Testlar ====================
@router.message(F.text == "📝 Testlar")
async def tests_info(message: types.Message, session: AsyncSession):
    stmt = select(func.count(TestResult.id)).where(
        TestResult.user_id == message.from_user.id,
        TestResult.status == "passed"
    )
    result = await session.execute(stmt)
    passed = result.scalar() or 0

    await message.answer(
        "📝 **Test bo'limi**\n\n"
        f"✅ O'tgan testlaringiz: **{passed}**\n\n"
        "**Baholash mezonlari:**\n"
        "🟢 80%+ = O'tdi\n"
        "🟡 60-79% = Qayta topshirish\n"
        "🔴 60% dan past = Mentor bilan qayta o'qish\n\n"
        "📌 Testlar kurs tugatilgandan so'ng ochiladi.",
        parse_mode="Markdown"
    )


# ==================== Sertifikatlarim ====================
@router.message(F.text == "🏆 Sertifikatlarim")
async def my_certificates(message: types.Message, session: AsyncSession):
    stmt = select(Certificate).where(Certificate.user_id == message.from_user.id)
    result = await session.execute(stmt)
    certs = result.scalars().all()

    if not certs:
        await message.answer(
            "🏆 **Sertifikatlar**\n\n"
            "Sizda hali sertifikat yo'q.\n"
            "Kurslarni muvaffaqiyatli tugatib, sertifikat oling!\n\n"
            "**Darajalar:**\n"
            "🥇 Oltin - 95%+\n"
            "🥈 Kumush - 85-94%\n"
            "🥉 Bronza - 80-84%",
            parse_mode="Markdown"
        )
        return

    text = "🏆 **Sizning sertifikatlaringiz:**\n\n"
    medals = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}
    for c in certs:
        medal = medals.get(c.level, "📜")
        text += f"{medal} Kurs #{c.course_id} — {c.issued_at.strftime('%d.%m.%Y')}\n"

    await message.answer(text, parse_mode="Markdown")


# ==================== Reytingim ====================
@router.message(F.text == "📈 Reytingim")
async def my_rating(message: types.Message, session: AsyncSession):
    # Calculate user's average test score
    stmt = select(func.avg(TestResult.score)).where(
        TestResult.user_id == message.from_user.id
    )
    result = await session.execute(stmt)
    avg_score = result.scalar()

    # Count completed courses
    stmt2 = select(func.count(CourseProgress.id)).where(
        CourseProgress.user_id == message.from_user.id,
        CourseProgress.completed_at.isnot(None)
    )
    result2 = await session.execute(stmt2)
    completed = result2.scalar() or 0

    avg_display = f"{avg_score:.0f}%" if avg_score else "—"

    await message.answer(
        "📊 **Sizning reytingingiz:**\n\n"
        f"📈 O'rtacha test natijasi: **{avg_display}**\n"
        f"✅ Tugatilgan kurslar: **{completed}**\n\n"
        "**Reyting turlari:**\n"
        "🏆 Top-10 xodim\n"
        "🏢 Top filial\n"
        "👨‍🏫 Top mentor",
        parse_mode="Markdown"
    )


# ==================== O'qitish rejam ====================
@router.message(F.text == "🗓 O'qitish rejam")
async def training_plan(message: types.Message):
    await message.answer(
        "🗓 **Onboarding rejangiz:**\n\n"
        "**1-kun** 📌\n"
        "• Kompaniya haqida\n"
        "• Missiya va qadriyatlar\n"
        "• Ichki tartib qoidalari\n\n"
        "**3-kun** 📌\n"
        "• Bo'lim bilan tanishuv\n"
        "• Lavozim yo'riqnomasi\n"
        "• Xizmat standartlari\n\n"
        "**7-kun** 📌\n"
        "• Amaliy topshiriqlar\n"
        "• Birinchi test\n\n"
        "**30-kun** 🎓\n"
        "• Yakuniy sertifikatsiya",
        parse_mode="Markdown"
    )


# ==================== Mentor bilan aloqa ====================
@router.message(F.text == "👨‍🏫 Mentor bilan aloqa")
async def contact_mentor(message: types.Message, session: AsyncSession):
    stmt = select(User).where(User.id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user and user.mentor_name:
        await message.answer(
            f"👨‍🏫 **Sizning mentoringiz:**\n\n"
            f"📝 Ism: **{user.mentor_name}**\n\n"
            "Savol yoki muammo bo'lsa, mentoringizga murojaat qiling!",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "👨‍🏫 Sizga hali mentor biriktirilmagan.\n"
            "HR bo'limiga murojaat qiling."
        )


# ==================== Savol berish ====================
@router.message(F.text == "💬 Savol berish")
async def ask_question(message: types.Message):
    await message.answer(
        "💬 **Savol berish**\n\n"
        "Savolingizni shu yerga yozing.\n"
        "Mentoringiz yoki HR tez orada javob beradi.\n\n"
        "📧 Yoki hr@company.uz ga yozing.",
        parse_mode="Markdown"
    )


# ==================== Baholash natijalari ====================
@router.message(F.text == "📋 Baholash natijalari")
async def assessment_results(message: types.Message, session: AsyncSession):
    stmt = select(TestResult).where(
        TestResult.user_id == message.from_user.id
    ).order_by(TestResult.completed_at.desc()).limit(10)
    result = await session.execute(stmt)
    results_list = result.scalars().all()

    if not results_list:
        await message.answer(
            "📋 **Baholash natijalari**\n\n"
            "Siz hali test topshirmagansiz.",
            parse_mode="Markdown"
        )
        return

    text = "📋 **Sizning baholash natijalaringiz:**\n\n"
    for r in results_list:
        status_icon = "✅" if r.status == "passed" else "🔄" if r.status == "retake" else "📖"
        text += f"{status_icon} Test #{r.test_id}: **{r.score:.0f}%** ({r.status})\n"

    await message.answer(text, parse_mode="Markdown")


# ==================== Karyera yo'li ====================
@router.message(F.text == "🏅 Karyera yo'li")
async def career_path(message: types.Message, session: AsyncSession):
    stmt = select(User).where(User.id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. /start ni bosing.")
        return

    career_steps = [
        ("Sotuvchi", "🟢"),
        ("Katta sotuvchi", "🔵"),
        ("Supervayzer", "🟡"),
        ("Filial rahbari", "🟠"),
        ("Hududiy rahbar", "🔴"),
    ]

    text = f"🏅 **{user.full_name} — Karyera yo'li**\n\n"
    text += f"📍 Hozirgi lavozim: **{user.position}**\n"
    text += f"🚀 Maqom: **{user.role.value.capitalize()}**\n\n"
    text += "**Rivojlanish yo'li:**\n\n"

    for title, icon in career_steps:
        marker = "👉 " if title.lower() in user.position.lower() else "   "
        text += f"{marker}{icon} {title}\n        ↓\n"

    text = text.rstrip("        ↓\n")
    text += "\n\n📌 Har bir bosqich uchun kerakli kurslar va testlar mavjud."

    await message.answer(text, parse_mode="Markdown")


# ==================== /help ====================
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "ℹ️ **Yordam**\n\n"
        "🤖 Ichki Akademiya boti yordamida siz:\n\n"
        "📚 Kurslarni ko'rishingiz\n"
        "📝 Testlar topshirishingiz\n"
        "🏆 Sertifikatlar olishingiz\n"
        "📈 Reytingingizni kuzatishingiz\n"
        "🗓 O'qitish rejangizni ko'rishingiz\n"
        "🏅 Karyera yo'lingizni bilishingiz mumkin.\n\n"
        "**Buyruqlar:**\n"
        "/start — Botni qayta ishga tushirish\n"
        "/profile — Profilim\n"
        "/help — Yordam",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
