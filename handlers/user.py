from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from config import config
from states import Quiz, Lead
from keyboards import main_menu, persona_keyboard, purpose_kb, functions_kb, business_kb, yes_no_kb, urgency_kb, confirm_kb, after_quiz_kb, ai_command_kb, quick_lead_kb
from database import save_application, save_visitor
from services.formatters import lead_summary, admin_lead_text
from services.ai_service import ai_answer, ask_ai
from services.google_sheets import send_to_sheets
from services.voice_service import transcribe_voice
from services.examples_service import load_examples, format_example

router = Router()

AI_SALES_RULES = "\n\nОбязательно используй фразы: «Начнём с 1000 грн» и «Финальная стоимость зависит от задач и будет согласована с разработчиком». Не используй калькулятор."

async def notify_new_visitor(bot: Bot, message: Message):
    username = f"@{message.from_user.username}" if message.from_user.username else "Не указано"
    text = ("👤 Новый посетитель бота\n\n"
            f"Имя: {message.from_user.first_name or 'Не указано'}\n"
            f"Username: {username}\n"
            f"Telegram ID: {message.from_user.id}\n"
            "Источник: Telegram")
    for admin_id in config.admin_ids:
        await bot.send_message(admin_id, text)

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    is_new = await save_visitor(message.from_user)
    if is_new:
        await notify_new_visitor(bot, message)
    await message.answer("Здравствуйте 👋\nНачнём с 1000 грн.\nФинальная стоимость зависит от задач и будет согласована с разработчиком.", reply_markup=main_menu())

@router.message(F.text == "🎙 AI-команда")
async def ai_command_start(message: Message, state: FSMContext):
    await state.update_data(ai_command_mode=True, ai_command_text="")
    await message.answer("Отправьте голосовое или текстовое сообщение.\nРасскажите, какой бот вам нужен, для какого бизнеса, какие функции нужны и как с вами связаться.")

@router.message(F.text == "🎯 Подобрать решение под мой бизнес")
async def pick_business(message: Message, state: FSMContext):
    await state.update_data(ai_command_mode=True)
    await message.answer("Напишите или отправьте голосом сферу бизнеса, и я предложу структуру бота.")

@router.message(F.text == "🎨 Примеры ботов")
async def examples(message: Message):
    items = load_examples()
    if not items:
        return await message.answer("Примеры пока не добавлены.")
    for i, ex in enumerate(items, 1):
        await message.answer(format_example(ex, i), parse_mode="HTML")
        await message.answer("Нажмите: Хочу такой бот", reply_markup=quick_lead_kb())

@router.message(F.text == "📝 Оформить заявку")
async def lead_start(message: Message, state: FSMContext):
    await state.clear(); await state.set_state(Lead.name)
    await message.answer("Как вас зовут?")

@router.message(Lead.name)
async def lead_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text); await state.set_state(Lead.phone); await message.answer("Введите номер телефона или Telegram для связи:")

@router.message(Lead.phone)
async def lead_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text); await state.set_state(Lead.business); await message.answer("Для какого бизнеса нужен бот?", reply_markup=business_kb())

@router.message(Lead.business)
async def lead_business(message: Message, state: FSMContext):
    await state.update_data(business=message.text); await state.set_state(Lead.bot_type); await message.answer("Какой бот нужен?", reply_markup=purpose_kb())

@router.message(Lead.bot_type)
async def lead_bot_type(message: Message, state: FSMContext):
    await state.update_data(bot_type=message.text); await state.set_state(Lead.functions); await message.answer("Какие функции нужны?", reply_markup=functions_kb())

@router.message(Lead.functions)
async def lead_functions(message: Message, state: FSMContext):
    await state.update_data(functions=message.text); await state.set_state(Lead.payments); await message.answer("Нужна ли оплата в боте?", reply_markup=yes_no_kb())

@router.message(Lead.payments)
async def lead_payments(message: Message, state: FSMContext):
    await state.update_data(payments=message.text); await state.set_state(Lead.ai_needed); await message.answer("Нужен AI-консультант?", reply_markup=yes_no_kb())

@router.message(Lead.ai_needed)
async def lead_ai(message: Message, state: FSMContext):
    await state.update_data(ai_needed=message.text); await state.set_state(Lead.urgency); await message.answer("По срокам?", reply_markup=urgency_kb())

@router.message(Lead.urgency)
async def lead_urgency(message: Message, state: FSMContext):
    await state.update_data(urgency=message.text); await state.set_state(Lead.comment); await message.answer("Комментарий:")

@router.message(Lead.comment)
async def lead_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data(); est = "Начнём с 1000 грн. Финальная стоимость зависит от задач и будет согласована с разработчиком."
    await state.set_state(Lead.confirm)
    await message.answer(lead_summary(data, est), reply_markup=confirm_kb())

@router.message(Lead.confirm, F.text == "✅ Отправить заявку")
@router.message(F.text == "✅ Отправить заявку")
async def lead_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    raw = data.get("ai_command_text", "")
    if not data.get("name"): data["name"] = "Не указано"
    if not data.get("phone"): data["phone"] = f"@{message.from_user.username}" if message.from_user.username else "Не указано"
    data.setdefault("business", "Не указано"); data.setdefault("bot_type", "Не указано"); data.setdefault("functions", "Не указано")
    data.setdefault("payments", "Не указано"); data.setdefault("ai_needed", "Не указано"); data.setdefault("urgency", "Обычный срок")
    data.setdefault("comment", raw or "Не указано")
    est = "Начнём с 1000 грн. Финальная стоимость зависит от задач и будет согласована с разработчиком."
    app_id = await save_application(message.from_user, data, est)
    for admin_id in config.admin_ids:
        await bot.send_message(admin_id, admin_lead_text(app_id, message.from_user, data, est))
    await message.answer("Заявка отправлена ✅", reply_markup=main_menu()); await state.clear()

@router.message(F.voice | F.audio)
async def voice_handler(message: Message, state: FSMContext, bot: Bot):
    text, err = await transcribe_voice(bot, message)
    if err:
        return await message.answer(err)
    await state.update_data(last_voice_text=text)
    fake = Message.model_validate({**message.model_dump(), "text": text})
    await free_text(fake, state)

@router.message(F.text)
async def free_text(message: Message, state: FSMContext):
    data = await state.get_data()
    if await state.get_state():
        return
    text = message.text or ""
    if data.get("ai_command_mode") or "бот" in text.lower() or "заявк" in text.lower():
        old = data.get("ai_command_text", "")
        merged = (old + "\n" + text).strip()
        await state.update_data(ai_command_text=merged)
        ans = await ai_answer(merged + AI_SALES_RULES)
        await message.answer(f"Я понял задачу 👍\n\n{ans}\n\nХотите отправить заявку разработчику?", reply_markup=ai_command_kb())
        return
    await message.answer("Выберите действие в меню 👇", reply_markup=main_menu())
