from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    full_name = State()
    phone = State()
    dob = State()
    branch = State()
    department = State()
    position = State()
    hire_date = State()
    manager = State()
    mentor = State()
