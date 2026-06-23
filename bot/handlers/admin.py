from aiogram import Router, types, F
import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import User, TestResult, UserRole
from sqlalchemy import select, func
from bot.utils.reporting import export_users_to_excel
from aiogram.types import FSInputFile, ReplyKeyboardRemove
import os
import logging

router = Router()
logger = logging.getLogger(__name__)

# Hardcoded Admin IDs for security
ADMIN_IDS = [6339752659, 7351189083] # Asosiy admin ID-lari

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

# Admin check decorator (internal)
def is_admin(user_id: int):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 **Admin Paneli**\n\n"
        "📊 /stats - Umumiy statistika\n"
        "📢 /broadcast - Barcha xodimlarga xabar yuborish\n"
        "👥 /users - Xodimlar ro'yxatini (Excel) yuklab olish\n"
        "🏠 /start - Asosiy menyunga qaytish",
        parse_mode="Markdown"
    )

@router.message(Command("stats"))
async def get_stats(message: types.Message, session):
    if not is_admin(message.from_user.id):
        return

    # Count users
    stmt_users = select(func.count(User.id))
    result_users = await session.execute(stmt_users)
    user_count = result_users.scalar()
    
    # Count tests
    stmt_tests = select(func.count(TestResult.id))
    result_tests = await session.execute(stmt_tests)
    test_count = result_tests.scalar()
    
    # Branch stats
    # (Optional: more complex queries can be added here)

    await message.answer(
        "📊 **Akademiya Statistikasi**\n\n"
        f"👥 Umumiy xodimlar: **{user_count}**\n"
        f"📝 Yakunlangan testlar: **{test_count}**\n"
        "🎓 Berilgan sertifikatlar: **0**",
        parse_mode="Markdown"
    )

@router.message(Command("users"))
async def users_report(message: types.Message, session):
    if not is_admin(message.from_user.id):
        return

    status_msg = await message.answer("⏳ Hisobot tayyorlanmoqda, iltimos kuting...")
    
    try:
        file_path = await export_users_to_excel(session)
        if os.path.exists(file_path):
            excel_file = FSInputFile(file_path)
            await message.answer_document(excel_file, caption="👥 Barcha ro'yxatdan o'tgan xodimlar ro'yxati.")
            # Clean up after sending
            # os.remove(file_path) 
        else:
            await message.answer("❌ Fayl yaratishda xatolik yuz berdi.")
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        await message.answer(f"❌ Hisobot tayyorlashda xatolik: {e}")

@router.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "📢 **Xabar yuborish bo'limi**\n\n"
        "Barcha xodimlarga yubormoqchi bo'lgan xabaringizni yozing.\n"
        "Bekor qilish uchun /cancel deb yozing.",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext, session):
    if message.text == "/cancel":
        await message.answer("❌ Xabar yuborish bekor qilindi.")
        await state.clear()
        return

    # Fetch all user IDs
    stmt = select(User.id).where(User.is_active == True)
    result = await session.execute(stmt)
    user_ids = result.scalars().all()

    count = 0
    await message.answer(f"⏳ {len(user_ids)} ta foydalanuvchiga xabar yuborilmoqda...")

    for user_id in user_ids:
        try:
            await message.bot.send_message(user_id, message.text)
            count += 1
            await asyncio.sleep(0.05) # Rate limiting
        except Exception:
            continue

    await message.answer(f"✅ Xabar muvaffaqiyatli yuborildi! ({count}/{len(user_ids)})")
    await state.clear()
