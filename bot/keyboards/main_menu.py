from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton(text="🎓 Mening kurslarim"), KeyboardButton(text="📚 Bilimlar bazasi")],
        [KeyboardButton(text="📝 Testlar"), KeyboardButton(text="🏆 Sertifikatlarim")],
        [KeyboardButton(text="📈 Reytingim"), KeyboardButton(text="🗓 O'qitish rejam")],
        [KeyboardButton(text="👨‍🏫 Mentor bilan aloqa"), KeyboardButton(text="💬 Savol berish")],
        [KeyboardButton(text="📋 Baholash natijalari"), KeyboardButton(text="🏅 Karyera yo'li")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_menu():
    keyboard = [
        [KeyboardButton(text="📊 Hisobotlar"), KeyboardButton(text="👥 Xodimlar")],
        [KeyboardButton(text="➕ Kurs qo'shish"), KeyboardButton(text="📝 Testlar yaratish")],
        [KeyboardButton(text="🏠 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_mentor_menu():
    keyboard = [
        [KeyboardButton(text="👥 Biriktirilgan stajerlar"), KeyboardButton(text="📊 Natijalar")],
        [KeyboardButton(text="📝 Baholash formasi"), KeyboardButton(text="🏠 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
