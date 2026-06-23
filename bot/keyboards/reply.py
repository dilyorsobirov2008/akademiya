from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.models import UserRole

def get_main_menu(role: UserRole = UserRole.STAGER):
    # Base menu for everyone
    buttons = [
        [KeyboardButton(text="🎓 Mening kurslarim"), KeyboardButton(text="📚 Bilimlar bazasi")],
        [KeyboardButton(text="📝 Testlar"), KeyboardButton(text="🏆 Sertifikatlarim")],
        [KeyboardButton(text="📈 Reytingim"), KeyboardButton(text="🗓 O'qitish rejam")],
        [KeyboardButton(text="👨‍🏫 Mentor bilan aloqa"), KeyboardButton(text="💬 Savol berish")],
        [KeyboardButton(text="📋 Baholash natijalari"), KeyboardButton(text="🏅 Karyera yo'li")]
    ]

    # Specific buttons for Admin/HR/Director
    if role in [UserRole.ADMIN, UserRole.HR, UserRole.DIRECTOR]:
        buttons.append([KeyboardButton(text="📊 Boshqaruv paneli")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_branches_kb():
    keyboard = [
        [KeyboardButton(text="Tasanno 1"), KeyboardButton(text="Tasanno 2")],
        [KeyboardButton(text="Bozorcha Supermarketi"), KeyboardButton(text="Bosh ofis")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_departments_kb():
    keyboard = [
        [KeyboardButton(text="Sotuv"), KeyboardButton(text="Kassa")],
        [KeyboardButton(text="Ombor"), KeyboardButton(text="Undiruv")],
        [KeyboardButton(text="HR"), KeyboardButton(text="IT")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
