from aiogram.fsm.state import StatesGroup, State

class Quiz(StatesGroup):
    purpose = State()
    functions = State()
    business = State()

class Demo(StatesGroup):
    business = State()

class Lead(StatesGroup):
    name = State()
    phone = State()
    business = State()
    bot_type = State()
    functions = State()
    payments = State()
    ai_needed = State()
    urgency = State()
    comment = State()
    confirm = State()

class VoiceLead(StatesGroup):
    waiting_voice = State()
    confirm = State()

class AdminEdit(StatesGroup):
    min_price = State()
    max_price = State()
    urgent_price = State()
    deadline = State()
    payment_terms = State()
    package_name = State()
    package_desc = State()
    example_title = State()
    example_desc = State()
