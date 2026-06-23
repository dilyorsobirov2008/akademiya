from aiogram import Router, types, F
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
    # Fetch tests from DB
    stmt = select(Test).join(Test.course).limit(5)
    result = await session.execute(stmt)
    tests = result.scalars().all()

    if not tests:
        await message.answer(
            "📝 **Hozirda mavjud testlar yo'q.**\n\n"
            "Onboarding jarayonida bo'lsangiz, 7-kundan keyin testlar ochiladi.",
            parse_mode="Markdown"
        )
        return

    text = "📝 **Mavjud Testlar:**\n\n"
    for i, test in enumerate(tests, 1):
        text += f"{i}. {test.title}\n"
    
    text += "\nTestni boshlash uchun uning tartib raqamini yozing (tez kunda to'liq ishga tushadi...)"
    await message.answer(text, parse_mode="Markdown")

# Future: Implement actual test engine here
