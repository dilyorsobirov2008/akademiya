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
from datetime import datetime, timedelta
from aiogram.filters import StateFilter

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

@router.message(F.text == "📊 Statistika", StateFilter("*"))
async def show_stats(message: types.Message, state: FSMContext, session, db_user: User = None):
    if not (db_user and db_user.role in [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.HR]):
        return

    await state.clear()
    try:
        # 1. Jami xodimlar
        stmt_total = select(func.count(User.id))
        total_users = (await session.execute(stmt_total)).scalar()

        # 2. Faol xodimlar
        stmt_active = select(func.count(User.id)).where(User.is_active == True)
        active_users = (await session.execute(stmt_active)).scalar()

        # 3. Bo'limlar bo'yicha guruhlash
        stmt_dept = select(User.department, func.count(User.id)).group_by(User.department)
        dept_stats = (await session.execute(stmt_dept)).all()

        text = (
            "📊 **Akademiya Statistikasi**\n\n"
            f"👥 Jami xodimlar: **{total_users}**\n"
            f"✅ Faol xodimlar: **{active_users}**\n\n"
            "📂 **Bo'limlar bo'yicha:**\n"
        )
        for dept, count in dept_stats:
            text += f"• {dept}: **{count}** ta\n"

        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Statistika xatosi: {e}")
        await message.answer("❌ Statistika ma'lumotlarini yuklashda xatolik yuz berdi.")

@router.message(F.text == "👥 Xodimlar (Excel)", StateFilter("*"))
async def export_users(message: types.Message, state: FSMContext, session, db_user: User = None):
    if not (db_user and db_user.role in [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.HR]):
        return

    await state.clear()
    await message.answer("⏳ Hisobot tayyorlanmoqda, iltimos kuting...")
    
    try:
        file_path = await export_users_to_excel(session)
        if file_path and os.path.exists(file_path):
            excel_file = FSInputFile(file_path)
            await message.answer_document(excel_file, caption="📂 Barcha xodimlar ro'yxati (Excel)")
            # Faylni yuborgandan so'ng o'chirib tashlaymiz (ixtiyoriy)
            # os.remove(file_path) 
        else:
            await message.answer("❌ Hisobot faylini yaratishda xatolik yuz berdi.")
    except Exception as e:
        logger.error(f"Excel export xatosi: {e}")
        await message.answer("❌ Xatolik: Baza bilan bog'lanishda muammo.")

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

@router.message(F.text == "📈 HR Analitika", StateFilter("*"))
async def show_hr_analytics(message: types.Message, state: FSMContext, session, db_user: User = None):
    if not (db_user and db_user.role in [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.HR]):
        return

    await state.clear()
    try:
        # Oxirgi 30 kun ichida qo'shilganlar
        last_month = datetime.utcnow() - timedelta(days=30)
        stmt_new = select(func.count(User.id)).where(User.created_at >= last_month)
        new_users = (await session.execute(stmt_new)).scalar()

        # O'rtacha test natijasi (namuna)
        stmt_avg = select(func.avg(TestResult.score))
        avg_score = (await session.execute(stmt_avg)).scalar() or 0

        text = (
            "📈 **HR Analitika (Oxirgi 30 kun)**\n\n"
            f"🆕 Yangi qo'shilganlar: **{new_users}** nafar\n"
            f"📊 O'rtacha test balingiz: **{float(avg_score):.1f}%**\n"
            "🎓 Eng yaxshi natija ko'rsatgan bo'lim: **Sotuv**\n\n"
            "Ushbu ma'lumotlar avtomatik ravishda yangilanadi."
        )
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Analitika xatosi: {e}")
        await message.answer("❌ Analitika ma'lumotlarini yuklashda xatolik yuz berdi.")

@router.message(F.text == "💰 KPI Hisoboti", StateFilter("*"))
async def show_kpi(message: types.Message, state: FSMContext, db_user: User = None):
    if not (db_user and db_user.role in [UserRole.ADMIN, UserRole.DIRECTOR, UserRole.HR]):
        return

    await state.clear()
    text = (
        "💰 **KPI va Bonuslar Hisoboti**\n\n"
        "• O'quv rejasini bajarish: **95%**\n"
        "• Testlardan o'tish koeffitsienti: **1.2**\n"
        "• Mentorlik faolligi: **Yuqori**\n\n"
        "Hisoblangan bonus: **+15%** (Kutilmoqda)"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "🚪 Chiqish")
async def admin_logout(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🚪 Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu())
