from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, UserRole
from bot.keyboards.reply import get_main_menu, get_branches_kb, get_departments_kb
from bot.utils.scheduler import schedule_onboarding
from datetime import datetime
import logging

router = Router()
logger = logging.getLogger(__name__)

class Registration(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_birth_date = State()
    waiting_for_branch = State()
    waiting_for_department = State()
    waiting_for_position = State()
    waiting_for_hire_date = State()
    waiting_for_manager = State()
    waiting_for_mentor = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, db_user: User = None):
    if db_user:
        await message.answer(
            f"👋 Qayta xush kelibsiz, **{db_user.full_name}**!\n"
            f"Sizning maqomingiz: **{db_user.role.value.capitalize()}**",
            reply_markup=get_main_menu(db_user.role),
            parse_mode="Markdown"
        )
        return

    await state.clear()
    await message.answer(
        "🌟 **Ichki Akademiya botiga xush kelibsiz!**\n\n"
        "Ro'yxatdan o'tish uchun F.I.Sh. (Familiya Ism Sharif) kiriting:"
    )
    await state.set_state(Registration.waiting_for_full_name)

@router.message(Registration.waiting_for_full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📞 Telefon raqamingizni kiriting (+998XXXXXXXXX):")
    await state.set_state(Registration.waiting_for_phone)

@router.message(Registration.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("📅 Tug'ilgan sanangizni kiriting (KK.OO.YYYY):")
    await state.set_state(Registration.waiting_for_birth_date)

@router.message(Registration.waiting_for_birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        await state.update_data(birth_date=birth_date)
        await message.answer("🏢 Filialingizni tanlang:", reply_markup=get_branches_kb())
        await state.set_state(Registration.waiting_for_branch)
    except ValueError:
        await message.answer("❌ Sana noto'g'ri kiritildi. KK.OO.YYYY formatida yozing (Masalan: 15.05.1995):")

@router.message(Registration.waiting_for_branch)
async def process_branch(message: types.Message, state: FSMContext):
    await state.update_data(branch=message.text)
    await message.answer("📂 Bo'limingizni tanlang:", reply_markup=get_departments_kb())
    await state.set_state(Registration.waiting_for_department)

@router.message(Registration.waiting_for_department)
async def process_department(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await message.answer("👔 Lavozimingizni kiriting:")
    await state.set_state(Registration.waiting_for_position)

@router.message(Registration.waiting_for_position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("📅 Ishga qabul qilingan sanangiz (KK.OO.YYYY):")
    await state.set_state(Registration.waiting_for_hire_date)

@router.message(Registration.waiting_for_hire_date)
async def process_hire_date(message: types.Message, state: FSMContext):
    try:
        hire_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        await state.update_data(hire_date=hire_date)
        await message.answer("👨‍💼 Bevosita rahbaringiz ismini kiriting:")
        await state.set_state(Registration.waiting_for_manager)
    except ValueError:
        await message.answer("❌ Sana noto'g'ri. KK.OO.YYYY formatida yozing:")

@router.message(Registration.waiting_for_manager)
async def process_manager(message: types.Message, state: FSMContext):
    await state.update_data(manager_name=message.text)
    await message.answer("👨‍🏫 Mentoringiz ismini kiriting (agar bo'lmasa 'Yo'q' deb yozing):")
    await state.set_state(Registration.waiting_for_mentor)

@router.message(Registration.waiting_for_mentor)
async def process_mentor(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    mentor_name = message.text if message.text.lower() != "yo'q" else None
    
    new_user = User(
        id=message.from_user.id,
        username=message.from_user.username,
        full_name=data['full_name'],
        phone=data['phone'],
        birth_date=data['birth_date'],
        branch=data['branch'],
        department=data['department'],
        position=data['position'],
        hire_date=data['hire_date'],
        manager_name=data['manager_name'],
        mentor_name=mentor_name,
        role=UserRole.STAGER
    )
    
    try:
        session.add(new_user)
        await session.commit()
        logger.info(f"✅ Yangi xodim ro'yxatdan o'tdi: {new_user.full_name} (ID: {new_user.id})")
        
        await message.answer(
            "✅ **Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!**\n\n"
            "Sizga 'Stajer' maqomi berildi. Akademiyada o'qishni boshlashingiz mumkin.",
            reply_markup=get_main_menu(UserRole.STAGER),
            parse_mode="Markdown"
        )
        await schedule_onboarding(message.bot, message.from_user.id)
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ DATABASE ERROR: {e}")
        await message.answer(
            "❌ **Ma'lumotlarni saqlashda xatolik!**\n\n"
            "Ehtimol ma'lumotlar bazasi eskirgan. Iltimos, admin bilan bog'laning yoki bir necha daqiqadan so'ng `/start` ni qayta bosing.",
            parse_mode="Markdown"
        )
    finally:
        await state.clear()
