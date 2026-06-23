from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton(text="📚 Kurslar"), KeyboardButton(text="📝 Testlar")],
        [KeyboardButton(text="🏆 Reyting"), KeyboardButton(text="🏅 Karyera yo'li")],
        [KeyboardButton(text="📜 Sertifikatlar")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_branches_kb():
    keyboard = [
        [KeyboardButton(text="Tasanno 1"), KeyboardButton(text="Tasanno 2")],
        [KeyboardButton(text="Bozorcha Supermarketi")],
        [KeyboardButton(text="Bosh ofis")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_departments_kb():
    keyboard = [
        [KeyboardButton(text="Ombor"), KeyboardButton(text="Sotuvchi")],
        [KeyboardButton(text="Kassa"), KeyboardButton(text="Qo'riqlash")],
        [KeyboardButton(text="HR"), KeyboardButton(text="IT")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
