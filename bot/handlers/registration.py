from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from bot.states.registration import Registration
from database.models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
import re
from datetime import datetime

router = Router()

def is_valid_date(date_str: str) -> bool:
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

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 **Assalomu alaykum!**\n\n"
        "Ichki Akademiya (Internal Academy) botiga xush kelibsiz.\n"
        "Tizimdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
        "👤 **F.I.Sh. (To'yxingizni kiriting):**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.full_name)

@router.message(Registration.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        "📞 **Telefon raqamingizni yuboring:**\n"
        "Pastdagi tugmani bosing yoki +998XXXXXXXXX formatida yozing.",
        reply_markup=get_contact_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.phone)

@router.message(Registration.phone, F.contact | F.text)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    if not re.match(r'^\+?998\d{9}$', phone.replace(" ", "")):
         await message.answer("❌ Noto'g'ri format. Iltimos, +998XXXXXXXXX formatida kiriting.")
         return
    
    await state.update_data(phone=phone)
    await message.answer(
        "📅 **Tug'ilgan sanangizni kiriting:**\n"
        "Format: KK.OO.YYYY (Masalan: 15.05.1995)",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.dob)

@router.message(Registration.dob)
async def process_dob(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Noto'g'ri sana kiritildi yoki kalendar bo'yicha bunday kun yo'q. Iltimos, KK.OO.YYYY formatida qayta kiriting (Masalan: 15.05.1995):")
        return
    
    await state.update_data(dob=message.text)
    await message.answer(
        "🏢 **Filialingizni tanlang yoki yozing:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.branch)

@router.message(Registration.branch)
async def process_branch(message: types.Message, state: FSMContext):
    await state.update_data(branch=message.text)
    await message.answer(
        "📂 **Bo'limingizni kiriting:**\n"
        "(Masalan: Sotuv, Kassa, IT)",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.department)

@router.message(Registration.department)
async def process_dept(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await message.answer(
        "👔 **Lavozimingizni kiriting:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.position)

@router.message(Registration.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer(
        "📅 **Ishga qabul qilingan sanangiz:**\n"
        "Format: KK.OO.YYYY",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.hire_date)

@router.message(Registration.hire_date)
async def process_hire_date(message: types.Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer("❌ Noto'g'ri sana kiritildi. KK.OO.YYYY formatida yozing (Masalan: 01.01.2024):")
        return
    
    await state.update_data(hire_date=message.text)
    await message.answer(
        "👨‍💼 **Bevosita rahbariingizning F.I.Sh:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.manager)

@router.message(Registration.manager)
async def process_manager(message: types.Message, state: FSMContext):
    await state.update_data(manager=message.text)
    await message.answer(
        "👨‍🏫 **Mentoringiz (ustozingiz) ning F.I.Sh:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.mentor)

@router.message(Registration.mentor)
async def process_mentor(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    
    # Convert string dates to date objects
    try:
        dob_date = datetime.strptime(data['dob'], '%d.%m.%Y').date()
        hire_date = datetime.strptime(data['hire_date'], '%d.%m.%Y').date()
    except ValueError:
        dob_date = None
        hire_date = datetime.now().date()

    # Save to DB
    try:
        new_user = User(
            id=message.from_user.id,
            full_name=data['full_name'],
            phone=data['phone'],
            dob=dob_date,
            branch=data['branch'],
            department=data['department'],
            position=data['position'],
            hire_date=hire_date,
            manager_name=data['manager'],
            role=UserRole.TRAINEE
        )
        
        session.add(new_user)
        await session.commit()
    except Exception as e:
        await session.rollback()
        await message.answer("❌ Ma'lumotlarni saqlashda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring yoki admin bilan bog'laning.")
        return

    await message.answer(
        "✅ **Tabriklayman!**\n\n"
        "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
        "Hozir siz **Stajer** maqomidasiz. Onboarding kurslari sizga ochildi.\n\n"
        "Boshlash uchun quyidagi menyudan foydalaning:",
        parse_mode="Markdown"
    )
    await state.clear()
    # Trigger menu showing logic here
