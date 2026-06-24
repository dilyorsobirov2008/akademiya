from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import Test, Question, TestResult
from sqlalchemy import select
import logging

router = Router()
logger = logging.getLogger(__name__)

class TestStates(StatesGroup):
    testing = State()

@router.message(F.text == "📝 Testlar")
async def show_available_tests(message: types.Message, session):
    # Filter by user category could be added here
    stmt = select(Test).limit(10)
    result = await session.execute(stmt)
    tests = result.scalars().all()

    if not tests:
        await message.answer(
            "📝 **Hozirda mavjud testlar yo'q.**\n\n"
            "T.Z. bo'yicha testlar 7 va 30-kunlarda avtomatik ochiladi.",
            parse_mode="Markdown"
        )
        return

    text = "📝 **Mavjud Testlar (T.Z. tizimi):**\n\n"
    for i, test in enumerate(tests, 1):
        text += f"{i}. {test.title} (Minimal: {test.min_score}%)\n"
    
    text += "\nTestni boshlash uchun tartib raqamini kiriting."
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📋 Baholash natijalari", StateFilter("*"))
async def show_test_results(message: types.Message, state: FSMContext, session):
    await state.clear()
    stmt = select(TestResult).where(TestResult.user_id == message.from_user.id).order_by(TestResult.finished_at.desc())
    result = await session.execute(stmt)
    results = result.scalars().all()
    
    if not results:
        await message.answer("Siz hali test topshirmagansiz.")
        return
        
    text = "📋 **Sizning natijalaringiz:**\n\n"
    for res in results:
        status = "✅ O'tdi" if res.is_passed else "❌ Qayta topshirish"
        text += f"📅 {res.finished_at.strftime('%d.%m.%Y')}: **{res.score}%** - {status}\n"
    
    await message.answer(text, parse_mode="Markdown")
