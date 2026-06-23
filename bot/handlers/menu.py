from aiogram import Router, types, F
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(F.text == "🎓 Mening kurslarim")
async def my_courses(message: types.Message):
    await message.answer(
        "📚 **Sizning faol kurslaringiz:**\n\n"
        "1. **Onboarding** (30% tugatildi)\n"
        "2. **Korporativ madaniyat** (Boshlanmagan)\n\n"
        "Kursni davom ettirish uchun bosing:",
        parse_mode="Markdown"
    )

@router.message(F.text == "📚 Bilimlar bazasi")
async def knowledge_base(message: types.Message):
    await message.answer(
        "📖 **Bilimlar bazasi**\n\n"
        "Kerakli bo'limni tanlang:\n"
        "📁 Qo'llanmalar\n"
        "📁 Video darslar\n"
        "📁 Standartlar",
        parse_mode="Markdown"
    )

@router.message(F.text == "📝 Testlar")
async def tests_list(message: types.Message):
    await message.answer(
        "📝 **Mavjud testlar:**\n\n"
        "• Haftalik test (7-kun)\n"
        "• Bilimni baholash\n\n"
        "Testni boshlash uchun kursni tugatgan bo'lishingiz kerak.",
        parse_mode="Markdown"
    )

@router.message(F.text == "📈 Reytingim")
async def my_rating(message: types.Message):
    await message.answer(
        "🏆 **Sizning reytingingiz:**\n\n"
        "📍 O'rningiz: **15-chi**\n"
        "⭐ Ballaringiz: **450**\n"
        "📊 O'rtacha test natijangiz: **85%**\n\n"
        "Top-10 ligaga kirish uchun yana 50 ball kerak!",
        parse_mode="Markdown"
    )
