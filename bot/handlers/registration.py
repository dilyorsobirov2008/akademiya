from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import Context
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from bot.states.registration import Registration
import re

router = Router()

def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: Context):
    await message.answer(
        "👋 **Assalomu alaykum!**\n\n"
        "Ichki Akademiya (Internal Academy) botiga xush kelibsiz.\n"
        "Tizimdan foydalanish uchun ro'yxatdan o'tishingiz kerak.\n\n"
        "👤 **F.I.Sh. (To'yxingizni kiriting):**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.full_name)

@router.message(Registration.full_name)
async def process_name(message: types.Message, state: Context):
    await state.update_data(full_name=message.text)
    await message.answer(
        "📞 **Telefon raqamingizni yuboring:**\n"
        "Pastdagi tugmani bosing yoki +998XXXXXXXXX formatida yozing.",
        reply_markup=get_contact_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(Registration.phone)

@router.message(Registration.phone, F.contact | F.text)
async def process_phone(message: types.Message, state: Context):
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
async def process_dob(message: types.Message, state: Context):
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        await message.answer("❌ Noto'g'ri format. KK.OO.YYYY formatida yozing.")
        return
    
    await state.update_data(dob=message.text)
    await message.answer(
        "🏢 **Filialingizni tanlang yoki yozing:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.branch)

@router.message(Registration.branch)
async def process_branch(message: types.Message, state: Context):
    await state.update_data(branch=message.text)
    await message.answer(
        "📂 **Bo'limingizni kiriting:**\n"
        "(Masalan: Sotuv, Kassa, IT)",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.department)

@router.message(Registration.department)
async def process_dept(message: types.Message, state: Context):
    await state.update_data(department=message.text)
    await message.answer(
        "👔 **Lavozimingizni kiriting:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.position)

@router.message(Registration.position)
async def process_position(message: types.Message, state: Context):
    await state.update_data(position=message.text)
    await message.answer(
        "📅 **Ishga qabul qilingan sanangiz:**\n"
        "Format: KK.OO.YYYY",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.hire_date)

@router.message(Registration.hire_date)
async def process_hire_date(message: types.Message, state: Context):
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        await message.answer("❌ Noto'g'ri format. KK.OO.YYYY formatida yozing.")
        return
    
    await state.update_data(hire_date=message.text)
    await message.answer(
        "👨‍💼 **Bevosita rahbariingizning F.I.Sh:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.manager)

@router.message(Registration.manager)
async def process_manager(message: types.Message, state: Context):
    await state.update_data(manager=message.text)
    await message.answer(
        "👨‍🏫 **Mentoringiz (ustozingiz) ning F.I.Sh:**",
        parse_mode="Markdown"
    )
    await state.set_state(Registration.mentor)

@router.message(Registration.mentor)
async def process_mentor(message: types.Message, state: Context):
    data = await state.get_data()
    # Here we would save to DB
    await message.answer(
        "✅ **Tabriklayman!**\n\n"
        "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
        "Hozir siz **Stajer** maqomidasiz. Onboarding kurslari sizga ochildi.\n\n"
        "Boshlash uchun quyidagi menyudan foydalaning:",
        parse_mode="Markdown"
    )
    await state.clear()
    # Trigger menu showing logic here
