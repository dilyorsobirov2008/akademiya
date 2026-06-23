from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, UserRole
from bot.keyboards.reply import get_main_menu, get_branches_kb, get_departments_kb
from bot.utils.scheduler import schedule_onboarding
import logging

router = Router()
logger = logging.getLogger(__name__)

class Registration(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_branch = State()
    waiting_for_department = State()
    waiting_for_position = State()
    waiting_for_manager = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, db_user: User = None):
    # Agar foydalanuvchi allaqachon bo'lsa, asosiy menyuni chiqarish
    if db_user:
        await message.answer(
            f"👋 Qayta xush kelibsiz, **{db_user.full_name}**!\n\n"
            f"Sizning maqomingiz: **{db_user.role.value.capitalize()}**\n"
            "Quyidagilardan birini tanlang:",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        await state.clear()
        return

    # Agar foydalanuvchi bo'lmasa, ro'yxatdan o'tishni boshlash
    await state.clear()
    welcome_text = (
        "🌟 **Ichki Akademiya (Internal Academy) botiga xush kelibsiz!**\n\n"
        "Sizni tizimda topa olmadik. Ro'yxatdan o'tishni boshlash uchun "
        "F.I.Sh. (Familiya Ism Sharif) kiriting:"
    )
    await message.answer(welcome_text, parse_mode="Markdown")
    await state.set_state(Registration.waiting_for_full_name)

@router.message(Registration.waiting_for_full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📞 Telefon raqamingizni kiriting (+998XXXXXXXXX formatda):")
    await state.set_state(Registration.waiting_for_phone)

@router.message(Registration.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏢 Filialingizni tanlang:", reply_markup=get_branches_kb())
    await state.set_state(Registration.waiting_for_branch)

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
    await message.answer("👨‍💼 Bevosita rahbaringiz ismini kiriting:")
    await state.set_state(Registration.waiting_for_manager)

@router.message(Registration.waiting_for_manager)
async def process_manager(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    
    # Create new user in DB
    new_user = User(
        id=message.from_user.id,
        username=message.from_user.username,
        full_name=data['full_name'],
        phone=data['phone'],
        branch=data['branch'],
        department=data['department'],
        position=data['position'],
        manager_name=message.text,
        role=UserRole.STAGER
    )
    
    try:
        session.add(new_user)
        await session.commit()
        
        await message.answer(
            "✅ **Muvaffaqiyatli ro'yxatdan o'tdingiz!**\n\n"
            "Sizga 'Stajer' maqomi berildi. Akademiyada o'qishni boshlashingiz mumkin.",
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
        
        # Schedule onboarding reminders
        await schedule_onboarding(message.bot, message.from_user.id)
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Registration Error: {e}")
        await message.answer("❌ Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.")
    
    await state.clear()
