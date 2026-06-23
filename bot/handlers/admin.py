from aiogram import Router, types, F
import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.models import User, TestResult
from sqlalchemy import select, func
from bot.utils.reporting import export_users_to_excel
from aiogram.types import FSInputFile
import os
import logging

router = Router()
logger = logging.getLogger(__name__)

# Hardcoded Admin Credentials
ADMIN_USERNAME = "feruza11"
ADMIN_PASSWORD = "1234"

class AdminStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    waiting_for_broadcast = State()
    is_logged_in = State() # persistent state for logged in admins

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Xodimlar (Excel)")],
        [KeyboardButton(text="📢 Xabar yuborish"), KeyboardButton(text="🚪 Chiqish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("admin"))
async def admin_panel_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Check session
    if data.get("admin_logged_in"):
        await message.answer(
            "🛠 **Admin Paneli**\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
        return

    # Start login process
    await message.answer("🔑 **Admin Panelga kirish**\n\nLogin (Username) kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminStates.waiting_for_username)

@router.message(AdminStates.waiting_for_username)
async def process_admin_username(message: types.Message, state: FSMContext):
    if message.text == ADMIN_USERNAME:
        await message.answer("✅ Username to'g'ri. Endi parolni kiriting:")
        await state.set_state(AdminStates.waiting_for_password)
    else:
        await message.answer("❌ Login yoki parol noto'g'ri. Qaytadan urinib ko'ring.\n\nLogin (Username) kiriting:")
        await state.set_state(AdminStates.waiting_for_username)

@router.message(AdminStates.waiting_for_password)
async def process_admin_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.update_data(admin_logged_in=True)
        await message.answer(
            "✅ Muvaffaqiyatli kirdingiz!\n\n🛠 **Admin Paneli** ochildi:",
            reply_markup=get_admin_keyboard()
        )
        await state.set_state(AdminStates.is_logged_in)
    else:
        await message.answer("❌ Login yoki parol noto'g'ri. Qaytadan urinib ko'ring.\n\nLogin (Username) kiriting:")
        await state.set_state(AdminStates.waiting_for_username)

@router.message(F.text == "📊 Statistika", AdminStates.is_logged_in)
async def get_stats(message: types.Message, session):
    # Count users
    stmt_users = select(func.count(User.id))
    result_users = await session.execute(stmt_users)
    user_count = result_users.scalar()
    
    # Count tests
    stmt_tests = select(func.count(TestResult.id))
    result_tests = await session.execute(stmt_tests)
    test_count = result_tests.scalar()
    
    await message.answer(
        "📊 **Akademiya Statistikasi**\n\n"
        f"👥 Umumiy xodimlar: **{user_count}**\n"
        f"📝 Yakunlangan testlar: **{test_count}**\n"
        "🎓 Berilgan sertifikatlar: **0**",
        parse_mode="Markdown"
    )

@router.message(F.text == "👥 Xodimlar (Excel)", AdminStates.is_logged_in)
async def users_report(message: types.Message, session):
    status_msg = await message.answer("⏳ Hisobot tayyorlanmoqda...")
    try:
        file_path = await export_users_to_excel(session)
        excel_file = FSInputFile(file_path)
        await message.answer_document(excel_file, caption="👥 Xodimlar ro'yxati.")
        await status_msg.delete()
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@router.message(F.text == "📢 Xabar yuborish", AdminStates.is_logged_in)
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer("📢 Xabar matnini kiriting (Bekor qilish uchun /cancel):")
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext, session):
    if message.text == "/cancel":
        await message.answer("❌ Bekor qilindi.", reply_markup=get_admin_keyboard())
        await state.set_state(AdminStates.is_logged_in)
        return

    stmt = select(User.id)
    result = await session.execute(stmt)
    user_ids = result.scalars().all()

    sent = 0
    await message.answer(f"⏳ {len(user_ids)} ta odamga yuborilmoqda...")
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, message.text)
            sent += 1
            await asyncio.sleep(0.05)
        except: continue

    await message.answer(f"✅ Yuborildi: {sent}/{len(user_ids)}", reply_markup=get_admin_keyboard())
    await state.set_state(AdminStates.is_logged_in)

@router.message(F.text == "🚪 Chiqish", AdminStates.is_logged_in)
async def admin_logout(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚪 Sessiya tugatildi. Admin panelga qayta kirish uchun /admin yozing.", reply_markup=ReplyKeyboardRemove())
