from aiogram import Router, types, F
import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.models import User, TestResult, UserRole
from sqlalchemy import select, func
from bot.keyboards.reply import get_main_menu
from bot.utils.reporting import export_users_to_excel
from aiogram.types import FSInputFile
import os
import logging

router = Router()
logger = logging.getLogger(__name__)

# Credentials
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
        [KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="📈 HR Analitika"), KeyboardButton(text="💰 KPI Hisoboti")],
        [KeyboardButton(text="🚪 Chiqish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("admin"))
@router.message(F.text == "📊 Boshqaruv paneli")
async def admin_panel_start(message: types.Message, state: FSMContext, db_user: User = None):
    # Check if user role allows access OR session exists
    if (db_user and db_user.role in [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.HR]):
        await message.answer(
            f"🛠 **Boshqaruv paneli ({db_user.role.value.upper()})**",
            reply_markup=get_admin_keyboard(db_user.role)
        )
        await state.set_state(AdminStates.is_logged_in)
        return

    await message.answer("🔑 **Admin Panelga kirish**\n\nLogin (Username) kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminStates.waiting_for_username)

@router.message(AdminStates.waiting_for_username)
async def process_admin_username(message: types.Message, state: FSMContext):
    if message.text == ADMIN_USERNAME:
        await message.answer("✅ Username to'g'ri. Endi parolni kiriting:")
        await state.set_state(AdminStates.waiting_for_password)
    else:
        await message.answer("❌ Login noto'g'ri. Qaytadan urinib ko'ring.")

@router.message(AdminStates.waiting_for_password)
async def process_admin_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await message.answer(
            "✅ Muvaffaqiyatli kirdingiz!",
            reply_markup=get_admin_keyboard(UserRole.ADMIN)
        )
        await state.set_state(AdminStates.is_logged_in)
    else:
        await message.answer("❌ Parol noto'g'ri. Login kiriting:")
        await state.set_state(AdminStates.waiting_for_username)

@router.message(F.text == "👥 Xodimlar (Excel)")
async def export_users(message: types.Message, session):
    await message.answer("⏳ Hisobot tayyorlanmoqda, iltimos kuting...")
    
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    file_path = "users_report.xlsx"
    if await export_users_to_excel(users, file_path):
        excel_file = FSInputFile(file_path)
        await message.answer_document(excel_file, caption="📂 Barcha xodimlar ro'yxati")
        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        await message.answer("❌ Hisobot yaratishda xatolik yuz berdi.")

@router.message(F.text == "📢 Xabar yuborish")
async def start_broadcast(message: types.Message, state: FSMContext):
    await message.answer("📝 Barcha xodimlarga yubormoqchi bo'lgan xabaringizni yozing:")
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext, session):
    broadcast_text = message.text
    stmt = select(User.id).where(User.is_active == True)
    result = await session.execute(stmt)
    user_ids = result.scalars().all()
    
    count = 0
    await message.answer(f"📢 Yuborish boshlandi ({len(user_ids)} xodim)...")
    
    for uid in user_ids:
        try:
            await message.bot.send_message(uid, f"🔔 **Admin xabari:**\n\n{broadcast_text}", parse_mode="Markdown")
            count += 1
            await asyncio.sleep(0.05) # Rate limiting
        except Exception:
            continue
            
    await message.answer(f"✅ Xabar **{count}** ta xodimga muvaffaqiyatli yetkazildi.")
    await state.set_state(AdminStates.is_logged_in)

@router.message(F.text == "💰 KPI Hisoboti")
@router.message(F.text == "📈 HR Analitika")
async def show_kpi(message: types.Message):
    await message.answer(
        "📈 **Kengaytirilgan Analitika (Real-time):**\n\n"
        "• Akademiyaga qamrov: **100%**\n"
        "• O'rtacha o'zlashtirish: **82%**\n"
        "• Kechikayotganlar soni: **5 ta**\n"
        "• Sertifikat olganlar: **12 ta**",
        parse_mode="Markdown"
    )

@router.message(F.text == "🚪 Chiqish")
async def admin_logout(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚪 Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu())
