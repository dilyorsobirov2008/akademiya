from aiogram import Router, types, F
from database.models import User
from sqlalchemy import select
from aiogram.filters import Command

router = Router()

@router.message(Command("profile"))
@router.message(F.text == "🏅 Karyera yo'li") 
async def show_profile(message: types.Message, session):
    stmt = select(User).where(User.id == message.from_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("Siz hali ro'yxatdan o'tmabsiz. /start ni bosing.")
        return

    profile_text = (
        f"👤 **Sizning Profilingiz:**\n\n"
        f"📝 F.I.Sh: **{user.full_name}**\n"
        f"📞 Tel: **{user.phone}**\n"
        f"🏢 Filial: **{user.branch}**\n"
        f"📂 Bo'lim: **{user.department}**\n"
        f"👔 Lavozim: **{user.position}**\n"
        f"📅 Ish boshlangan: **{user.hire_date.strftime('%d.%m.%Y') if user.hire_date else '—'}**\n"
        f"👨‍💼 Rahbar: **{user.manager_name}**\n"
        f"👨‍🏫 Mentor: **{user.mentor_name if user.mentor_name else '—'}**\n"
        f"🚀 Maqomingiz: **{user.role.value.capitalize()}**"
    )
    
    await message.answer(profile_text, parse_mode="Markdown")
