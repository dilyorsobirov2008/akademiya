from aiogram import Router, types, F
import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.models import User, TestResult, UserRole
from sqlalchemy import select, func
from bot.utils.reporting import export_users_to_excel
from aiogram.types import FSInputFile
import os
import logging

router = Router()
logger = logging.getLogger(__name__)

# Hardcoded Admin Credentials (T.Z. base)
ADMIN_USERNAME = "feruza11"
ADMIN_PASSWORD = "1234"

class AdminStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    waiting_for_broadcast = State()
    is_logged_in = State()

def get_admin_keyboard(role: UserRole):
    keyboard = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Xodimlar (Excel)")],
        [KeyboardButton(text="📢 Xabar yuborish")]
    ]
    if role in [UserRole.ADMIN, UserRole.DIRECTOR]:
        keyboard.append([KeyboardButton(text="📈 HR Analitika"), KeyboardButton(text="💰 KPI Hisoboti")])
    
    keyboard.append([KeyboardButton(text="🚪 Chiqish")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("admin"))
@router.message(F.text == "📊 Boshqaruv paneli")
async def admin_panel_start(message: types.Message, state: FSMContext, db_user: User = None):
    data = await state.get_data()
    # Check session
    if data.get("admin_logged_in") or (db_user and db_user.role in [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.HR]):
        role = db_user.role if db_user else UserRole.ADMIN
        await message.answer(
            f"🛠 **Boshqaruv paneli ({role.value.upper()})**\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=get_admin_keyboard(role),
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
        await message.answer("❌ Login noto'g'ri. Qaytadan urinib ko'ring.\n\nLogin kiriting:")

@router.message(AdminStates.waiting_for_password)
async def process_admin_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.update_data(admin_logged_in=True)
        await message.answer(
            "✅ Muvaffaqiyatli kirdingiz!\n\n🛠 **Admin Paneli** ochildi:",
            reply_markup=get_admin_keyboard(UserRole.ADMIN)
        )
        await state.set_state(AdminStates.is_logged_in)
    else:
        await message.answer("❌ Parol noto'g'ri. Login kiriting:")
        await state.set_state(AdminStates.waiting_for_username)

@router.message(F.text == "📊 Statistika")
async def get_stats(message: types.Message, session, state: FSMContext):
    data = await state.get_data()
    if not data.get("admin_logged_in"):
        # This could also check db_user.role
        pass
        
    stmt_users = select(func.count(User.id))
    result_users = await session.execute(stmt_users)
    user_count = result_users.scalar()
    
    await message.answer(
        "📊 **Akademiya Statistikasi (T.Z. KPI)**\n\n"
        f"👥 Umumiy xodimlar: **{user_count}**\n"
        "🎓 Kursni tugatish: **0%**\n"
        "📝 O'rtacha test bali: **0%**\n"
        "📉 Turnover: **0%**",
        parse_mode="Markdown"
    )

@router.message(F.text == "🚪 Chiqish")
async def admin_logout(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚪 Sessiya tugatildi. Asosiy menyuga qaytasiz.", reply_markup=ReplyKeyboardRemove())
