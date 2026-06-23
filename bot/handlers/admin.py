from aiogram import Router, types, F
from aiogram.filters import Command
from database.models import User, TestResult
from sqlalchemy import select, func

router = Router()

# Admin check decorator or middleware would be better, but for now:
ADMIN_IDS = [12345678] # Replace with real admin IDs

@router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
async def admin_panel(message: types.Message):
    await message.answer(
        "🛠 **Admin Paneli**\n\n"
        "📊 /stats - Umumiy statistika\n"
        "📢 /broadcast - Xabar yuborish\n"
        "👥 /users - Xodimlar ro'yxati",
        parse_mode="Markdown"
    )

@router.message(Command("stats"), F.from_user.id.in_(ADMIN_IDS))
async def get_stats(message: types.Message, session):
    # Count users
    stmt = select(func.count(User.id))
    result = await session.execute(stmt)
    user_count = result.scalar()
    
    # Count tests
    stmt_tests = select(func.count(TestResult.id))
    result_tests = await session.execute(stmt_tests)
    test_count = result_tests.scalar()
    
    await message.answer(
        "📊 **Akademiya Statistikasi**\n\n"
        f"👥 Umumiy xodimlar: **{user_count}**\n"
        f"📝 Yakunlangan testlar: **{test_count}**\n"
        "🎓 Sertifikatlar: **0**",
        parse_mode="Markdown"
    )
