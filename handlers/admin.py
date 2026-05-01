from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import config
from states import AdminEdit
from keyboards import admin_menu, main_menu, admin_application_kb
from database import (
    get_recent_applications, update_status, stats, get_all_settings, set_setting,
    get_packages, add_package, get_examples, add_example
)

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids

@router.message(Command("admin"))
async def admin_start(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("Нет доступа.")
    await message.answer("Админ-панель открыта.", reply_markup=admin_menu())

@router.message(F.text == "⬅️ В меню")
async def back_menu(message: Message):
    await message.answer("Главное меню", reply_markup=main_menu())

@router.message(F.text == "🆕 Новые заявки")
async def apps(message: Message):
    if not is_admin(message.from_user.id): return
    rows = await get_recent_applications(10)
    if not rows:
        return await message.answer("Заявок пока нет.")
    for app_id, name, phone, business, bot_type, status, created_at in rows:
        await message.answer(
            f"Заявка №{app_id}\n"
            f"Дата: {created_at}\n"
            f"Имя: {name}\nТелефон: {phone}\n"
            f"Бизнес: {business}\nТип: {bot_type}\n"
            f"Статус: {status}",
            reply_markup=admin_application_kb(app_id)
        )

@router.callback_query(F.data.startswith("status:"))
async def set_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    _prefix, app_id, status = callback.data.split(":", 2)
    await update_status(int(app_id), status)
    await callback.answer("Статус обновлен")
    await callback.message.answer(f"Заявка №{app_id}: статус → {status}")

@router.message(F.text == "📊 Статистика")
async def show_stats(message: Message):
    if not is_admin(message.from_user.id): return
    s = await stats()
    await message.answer(
        "📊 Статистика:\n\n"
        f"Клиентов: {s['clients']}\n"
        f"Заявок: {s['apps']}\n"
        f"Срочных заявок: {s['urgent']}\n"
        f"Заявок с AI: {s['ai']}"
    )

@router.message(F.text == "💰 Настроить цены")
async def price_settings(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    s = await get_all_settings()
    await message.answer(
        "Текущие настройки:\n\n"
        f"СТАРТ от: {s.get('min_price')} грн\n"
        f"Предел расчета: {s.get('max_price')} грн\n"
        f"Срочность: +{s.get('urgent_price')} грн\n"
        f"Срок: {s.get('deadline')}\n\n"
        "Введите новую стартовую цену, например 1000:"
    )
    await state.set_state(AdminEdit.min_price)

@router.message(AdminEdit.min_price)
async def edit_min(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await set_setting("min_price", message.text.strip())
    await message.answer("Введите предел предварительного расчета, например 4500:")
    await state.set_state(AdminEdit.max_price)

@router.message(AdminEdit.max_price)
async def edit_max(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await set_setting("max_price", message.text.strip())
    await message.answer("Введите доплату за срочность, например 1000:")
    await state.set_state(AdminEdit.urgent_price)

@router.message(AdminEdit.urgent_price)
async def edit_urgent(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await set_setting("urgent_price", message.text.strip())
    await message.answer("Введите срок выполнения, например: 1–2 дня")
    await state.set_state(AdminEdit.deadline)

@router.message(AdminEdit.deadline)
async def edit_deadline(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await set_setting("deadline", message.text.strip())
    await state.clear()
    await message.answer("Цены и сроки обновлены ✅", reply_markup=admin_menu())

@router.message(F.text == "⚙️ Настройки")
async def terms_settings(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await message.answer("Введите новый текст условий оплаты:")
    await state.set_state(AdminEdit.payment_terms)

@router.message(AdminEdit.payment_terms)
async def edit_terms(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await set_setting("payment_terms", message.text.strip())
    await state.clear()
    await message.answer("Условия оплаты обновлены ✅", reply_markup=admin_menu())

@router.message(F.text == "📦 Пакеты")
async def packages(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    rows = await get_packages()
    text = "📦 Пакеты:\n\n" + "\n\n".join([f"{i}. {name}\n{desc}" for i, (_id, name, desc) in enumerate(rows, 1)])
    text += "\n\nЧтобы добавить пакет, отправьте название нового пакета."
    await message.answer(text)
    await state.set_state(AdminEdit.package_name)

@router.message(AdminEdit.package_name)
async def package_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.update_data(package_name=message.text.strip())
    await message.answer("Введите описание пакета:")
    await state.set_state(AdminEdit.package_desc)

@router.message(AdminEdit.package_desc)
async def package_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()
    await add_package(data["package_name"], message.text.strip())
    await state.clear()
    await message.answer("Пакет добавлен ✅", reply_markup=admin_menu())

@router.message(F.text == "🎨 Примеры")
async def admin_examples(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    rows = await get_examples()
    text = "🎨 Примеры:\n\n" + "\n\n".join([f"{i}. {title}\n{desc}" for i, (_id, title, desc) in enumerate(rows, 1)])
    text += "\n\nЧтобы добавить пример, отправьте название нового примера."
    await message.answer(text)
    await state.set_state(AdminEdit.example_title)

@router.message(AdminEdit.example_title)
async def example_title(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.update_data(example_title=message.text.strip())
    await message.answer("Введите описание примера:")
    await state.set_state(AdminEdit.example_desc)

@router.message(AdminEdit.example_desc)
async def example_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()
    await add_example(data["example_title"], message.text.strip())
    await state.clear()
    await message.answer("Пример добавлен ✅", reply_markup=admin_menu())
