from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from bot.states.registration import Registration
from bot.keyboards.main_menu import get_main_menu
from database.models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import re
import logging

router = Router()
logger = logging.getLogger(__name__)


def is_valid_date(date_str: str) -> bool:
    """Sanani to'g'riligini tekshirish (30.02 kabi noto'g'ri sanalarni rad etadi)."""
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False


def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


BRANCHES = ["Tasanno", "Bozorcha", "Boshqa"]

def get_branch_keyboard():
    buttons = [[KeyboardButton(text=b)] for b in BRANCHES]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


ROLES_LIST = [
    "Stajer (Yangi xodim)", "Xodim", "Mentor",
    "Filial rahbari", "HR", "Akademiya administratori", "Direktor"
]

ROLE_MAP = {
    "Stajer (Yangi xodim)": UserRole.TRAINEE,
    "Xodim": UserRole.EMPLOYEE,
    "Mentor": UserRole.MENTOR,
    "Filial rahbari": UserRole.BRANCH_MANAGER,
    "HR": UserRole.HR,
    "Akademiya administratori": UserRole.ADMIN,
    "Direktor": UserRole.DIRECTOR,
}

def get_role_keyboard():
    buttons = [[KeyboardButton(text=r)] for r in ROLES_LIST]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


# ==================== /start ====================
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    # Check if user already registered
    stmt = select(User).where(User.id == message.from_user.id)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        await message.answer(
            f"👋 Qayta xush kelibsiz, **{existing_user.full_name}**!\n\n"
            f"Sizning maqomingiz: **{existing_user.role.value.capitalize()}**\n"
            "Quyidagi menyudan foydalaning:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        await state.clear()
        return

    await message.answer(
        "👋 **Assalomu alaykum!**\n\n"
        "🎓 Ichki Akademiya (Internal Academy) botiga xush kelibsiz.\n"
        "Tizimdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
        "👤 **F.I.Sh. (To'liq ismingizni kiriting):**",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.full_name)


# ==================== F.I.Sh ====================
@router.message(Registration.full_name)
async def process_name(message: types.Message, state: FSMContext):
    if len(message.text.strip()) < 3:
        await message.answer("❌ Ism juda qisqa. Iltimos, to'liq F.I.Sh kiriting.")
        return
    await state.update_data(full_name=message.text.strip())
    await message.answer(
        "📞 **Telefon raqamingizni yuboring:**\n"
        "Pastdagi tugmani bosing yoki +998XXXXXXXXX formatida yozing.",
        reply_markup=get_contact_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.phone)


# ==================== Telefon ====================
@router.message(Registration.phone, F.contact | F.text)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    cleaned = phone.replace(" ", "").replace("-", "")
    if not re.match(r'^\+?998\d{9}$', cleaned):
        await message.answer("❌ Noto'g'ri format. Iltimos, +998XXXXXXXXX formatida kiriting.")
        return
    await state.update_data(phone=cleaned)
    await message.answer(
        "📅 **Tug'ilgan sanangizni kiriting:**\n"
        "Format: KK.OO.YYYY (Masalan: 15.05.1995)",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.dob)


# ==================== Tug'ilgan sana ====================
@router.message(Registration.dob)
async def process_dob(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer(
            "❌ Noto'g'ri sana! Kalendar bo'yicha bunday kun yo'q.\n"
            "Iltimos, KK.OO.YYYY formatida qayta kiriting (Masalan: 15.05.1995):"
        )
        return
    await state.update_data(dob=message.text)
    await message.answer(
        "🏢 **Filialingizni tanlang:**",
        reply_markup=get_branch_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.branch)


# ==================== Filial ====================
@router.message(Registration.branch)
async def process_branch(message: types.Message, state: FSMContext):
    await state.update_data(branch=message.text.strip())
    await message.answer(
        "📂 **Bo'limingizni kiriting:**\n"
        "(Masalan: Sotuv, Kassa, IT, Ombor)",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.department)


# ==================== Bo'lim ====================
@router.message(Registration.department)
async def process_dept(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text.strip())
    await message.answer(
        "👔 **Lavozimingizni kiriting:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.position)


# ==================== Lavozim ====================
@router.message(Registration.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text.strip())
    await message.answer(
        "📅 **Ishga qabul qilingan sanangiz:**\n"
        "Format: KK.OO.YYYY (Masalan: 01.06.2024)",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.hire_date)


# ==================== Ishga kirgan sana ====================
@router.message(Registration.hire_date)
async def process_hire_date(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer(
            "❌ Noto'g'ri sana! KK.OO.YYYY formatida yozing (Masalan: 01.01.2024):"
        )
        return
    await state.update_data(hire_date=message.text)
    await message.answer(
        "👨‍💼 **Bevosita rahbaringizning F.I.Sh:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.manager)


# ==================== Rahbar ====================
@router.message(Registration.manager)
async def process_manager(message: types.Message, state: FSMContext):
    await state.update_data(manager=message.text.strip())
    await message.answer(
        "👨‍🏫 **Mentoringiz (ustozingiz)ning F.I.Sh:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.mentor)


# ==================== Mentor (oxirgi qadam) ====================
@router.message(Registration.mentor)
async def process_mentor(message: types.Message, state: FSMContext, session: AsyncSession):
    mentor_name = message.text.strip()
    data = await state.get_data()

    # Convert dates
    try:
        dob_date = datetime.strptime(data['dob'], '%d.%m.%Y').date()
    except (ValueError, KeyError):
        dob_date = None

    try:
        hire_date = datetime.strptime(data['hire_date'], '%d.%m.%Y').date()
    except (ValueError, KeyError):
        hire_date = datetime.now().date()

    # Save to DB
    try:
        new_user = User(
            id=message.from_user.id,
            full_name=data.get('full_name', 'Nomaʼlum'),
            phone=data.get('phone', ''),
            dob=dob_date,
            branch=data.get('branch', ''),
            department=data.get('department', ''),
            position=data.get('position', ''),
            hire_date=hire_date,
            manager_name=data.get('manager', ''),
            mentor_name=mentor_name,
            role=UserRole.TRAINEE
        )
        session.add(new_user)
        await session.commit()
        logger.info(f"✅ Yangi foydalanuvchi: {new_user.full_name} (ID: {new_user.id})")
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ DB saqlash xatosi: {e}", exc_info=True)
        await message.answer(
            "❌ Ma'lumotlarni saqlashda xatolik yuz berdi.\n"
            "Iltimos, /start buyrug'ini qayta bosing.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return

    # Summary
    await message.answer(
        "✅ **Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!**\n\n"
        f"👤 Ism: **{data.get('full_name')}**\n"
        f"🏢 Filial: **{data.get('branch')}**\n"
        f"👔 Lavozim: **{data.get('position')}**\n"
        f"🚀 Maqom: **Stajer**\n\n"
        "Onboarding kurslari sizga ochildi.\n"
        "Quyidagi menyudan foydalaning:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await state.clear()

    # Schedule onboarding reminders
    try:
        from bot.utils.scheduler import schedule_onboarding
        schedule_onboarding(message.bot, message.from_user.id)
    except Exception as e:
        logger.warning(f"Onboarding scheduler xatosi: {e}")
