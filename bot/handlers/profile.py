from aiogram import Router, types, F
from database.models import User
from sqlalchemy import select

router = Router()

@router.message(F.text == "🏅 Karyera yo'li") # Using one of the menu buttons or we can add a new one
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
        f"📅 Ish boshlangan: **{user.hire_date}**\n"
        f"👨‍💼 Rahbar: **{user.manager_name}**\n"
        f"🚀 Maqomingiz: **{user.role.value.capitalize()}**"
    )
    
    await message.answer(profile_text, parse_mode="Markdown")
