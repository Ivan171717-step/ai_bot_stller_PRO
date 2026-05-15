from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import config
from states import Quiz, Lead
from keyboards import (
    admin_menu,
    main_menu,
    persona_keyboard,
    purpose_kb,
    functions_kb,
    business_kb,
    yes_no_kb,
    urgency_kb,
    confirm_kb,
    after_quiz_kb,
    ai_command_kb,
    quick_lead_kb,
)
from database import (
    save_application,
    save_visitor,
    export_applications_csv,
    export_visitors_csv,
    stats,
    visitor_stats,
    get_recent_visitors,
    get_recent_applications,
)
from services.formatters import lead_summary, admin_lead_text, internal_admin_note_text
from services.ai_service import ai_answer, ask_ai
from services.google_sheets import send_to_sheets
from services.voice_service import transcribe_voice
from services.examples_service import load_examples, format_example, search_examples
from services.assistant_router import detect_command
from services.lead_parser import parse_quick_lead, build_quick_lead_preview
from services.internal_analysis import analyze_internal_complexity

router = Router()

WELCOME = (
    "Здравствуйте 👋\n\n"
    "Я AI-консультант по созданию Telegram-ботов для бизнеса.\n"
    "Помогу понять, какой бот подойдет именно вам, и оформить заявку.\n\n"
    "Начнём с 1000 грн.\n"
    "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
    "Выберите действие ниже 👇"
)

AI_SALES_RULES = (
    "\n\nПравила ответа:\n"
    "1. Веди диалог как AI-консультант по разработке Telegram-ботов.\n"
    "2. Мягко веди клиента к конкретному следующему действию.\n"
    "3. Если нужно перейти к разделу, попроси клиента самостоятельно нажать нужную кнопку.\n"
    "4. Используй фразу: «Начнём с 1000 грн».\n"
    "5. Всегда добавляй: «Финальная стоимость зависит от задач и будет согласована с разработчиком».\n"
    "6. Не делай калькулятор и не указывай цены за отдельные функции.\n"
)


def examples_inline_from_files(items: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for ex in items:
        slug = ex.get("_slug", "")
        title = ex.get("title", "Пример")
        rows.append([InlineKeyboardButton(text=f"Хочу такой: {title}", callback_data=f"want_json_example:{slug}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def notify_new_visitor(bot: Bot, message: Message):
    username = f"@{message.from_user.username}" if message.from_user.username else "Не указано"
    text = (
        "👤 Новый посетитель бота\n\n"
        f"Имя: {message.from_user.first_name or 'Не указано'}\n"
        f"Username: {username}\n"
        f"Telegram ID: {message.from_user.id}\n"
        "Источник: Telegram"
    )
    for admin_id in config.admin_ids:
        await bot.send_message(admin_id, text)


async def send_application(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    raw = data.get("ai_command_text", "")

    if not data.get("name"):
        data["name"] = "Не указано"
    if not data.get("phone"):
        data["phone"] = f"@{message.from_user.username}" if message.from_user.username else "Не указано"

    data.setdefault("business", "Не указано")
    data.setdefault("bot_type", "Не указано")
    data.setdefault("functions", "Не указано")
    data.setdefault("payments", "Не указано")
    data.setdefault("ai_needed", "Не указано")
    data.setdefault("urgency", "Обычный срок")
    data.setdefault("comment", raw or "Не указано")

    estimated = "Начнём с 1000 грн. Финальная стоимость зависит от задач и будет согласована с разработчиком."
    app_id = await save_application(message.from_user, data, estimated)

    send_to_sheets("application", {
        "app_id": app_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username or "",
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "business": data.get("business", ""),
        "bot_type": data.get("bot_type", ""),
        "functions": data.get("functions", ""),
        "payments": data.get("payments", ""),
        "ai_needed": data.get("ai_needed", ""),
        "urgency": data.get("urgency", ""),
        "comment": data.get("comment", ""),
        "price": estimated,
    })

    analysis = analyze_internal_complexity(data)
    internal_note = internal_admin_note_text(analysis)
    for admin_id in config.admin_ids:
        await bot.send_message(admin_id, admin_lead_text(app_id, message.from_user, data, estimated, internal_note))

    await message.answer(
        "Заявка отправлена ✅\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.",
        reply_markup=main_menu(),
    )
    await state.clear()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    is_new = await save_visitor(message.from_user)
    if is_new:
        await notify_new_visitor(bot, message)

    send_to_sheets("visitor", {
        "user_id": message.from_user.id,
        "username": message.from_user.username or "",
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
        "source": "telegram"
    })

    banner = "assets/banner.png"
    try:
        await message.answer_photo(FSInputFile(banner), caption=WELCOME, reply_markup=main_menu())
    except Exception:
        await message.answer(WELCOME, reply_markup=main_menu())


@router.message(F.text == "⬅️ В меню")
async def menu_back(message: Message, state: FSMContext):
    await state.update_data(ai_chat_active=False, ai_command_mode=False)
    await message.answer("Главное меню 👇", reply_markup=main_menu())


@router.message(F.text == "🤖 Какой вам нужен бот")
async def quiz_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Давайте быстро поймем задачу.\n\nДля чего вам нужен бот?", reply_markup=purpose_kb())
    await state.set_state(Quiz.purpose)


@router.message(Quiz.purpose)
async def quiz_purpose(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(purpose=message.text)
    await message.answer("Какие функции нужны?\n\nМожно выбрать кнопку или написать своими словами.", reply_markup=functions_kb())
    await state.set_state(Quiz.functions)


@router.message(Quiz.functions)
async def quiz_functions(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(functions=message.text)
    await message.answer("Под какой бизнес нужен бот?", reply_markup=business_kb())
    await state.set_state(Quiz.business)


@router.message(Quiz.business)
async def quiz_business(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(business=message.text)
    data = await state.get_data()
    await state.clear()
    await message.answer(
        f"Отлично 👍\n\nЗадача: {data.get('purpose')}\n"
        f"Функции/пожелания: {data.get('functions')}\n"
        f"Бизнес: {data.get('business')}\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
        "Чтобы перейти дальше — нажмите кнопку «Оформить заявку».",
        reply_markup=after_quiz_kb(),
    )


@router.message(F.text == "🧠 AI-консультант")
async def choose_ai_persona(message: Message, state: FSMContext):
    await state.update_data(ai_chat_active=False)
    await message.answer(
        "Выберите стиль AI-консультанта 👇\n\n"
        "🌸 Анастейша — мягко, дружелюбно и понятно\n"
        "🧔 Джейсон — уверенно, по делу и с лёгким юмором\n"
        "🤖 Стандартный — спокойно и нейтрально",
        reply_markup=persona_keyboard(),
    )


@router.callback_query(F.data.startswith("persona:"))
async def set_persona(callback: CallbackQuery, state: FSMContext):
    persona = callback.data.split(":")[1]
    await state.update_data(ai_persona=persona, ai_chat_active=True)
    await callback.message.answer(
        "Отлично. Расскажите про ваш бизнес и задачи для бота.\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.",
        reply_markup=main_menu(),
    )
    await callback.answer()


@router.message(F.text == "🏢 Под какой бизнес")
async def business_info(message: Message):
    await message.answer(
        "Ботов можно сделать почти под любой бизнес: услуги, магазины, доставка, обучение, запись клиентов, металлолом, недвижимость, авто.\n\n"
        "Чтобы я задал несколько вопросов — нажмите «Какой вам нужен бот».\n"
        "Если уже готовы — нажмите «Оформить заявку».",
        reply_markup=main_menu(),
    )


@router.message(F.text == "🎙 AI-команда")
async def ai_command_start(message: Message, state: FSMContext):
    await state.update_data(ai_command_mode=True, ai_command_text="")
    await message.answer(
        "Отправьте голосовое или текстовое сообщение.\n"
        "Расскажите, какой бот вам нужен, для какого бизнеса, какие функции нужны и как с вами связаться.",
        reply_markup=ai_command_kb(),
    )


@router.message(F.text == "✏️ Дополнить голосом")
@router.message(F.text == "🎙 Добавить детали голосом")
async def ai_command_add_details(message: Message, state: FSMContext):
    await state.update_data(ai_command_mode=True)
    await message.answer("Отправьте дополнительные детали голосом или текстом — я обновлю разбор задачи.")


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

    await message.answer("Выберите пример, который вам ближе 👇", reply_markup=examples_inline_from_files(items))


@router.callback_query(F.data.startswith("want_json_example:"))
async def want_json_example(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split(":", 1)[1]
    selected = next((x for x in load_examples() if x.get("_slug") == slug), None)
    title = selected.get("title", "Пример") if selected else "Пример"
    await state.update_data(bot_type=title)
    await callback.message.answer(
        f"Отличный выбор: {title}.\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
        "Как вас зовут?"
    )
    await state.set_state(Lead.name)
    await callback.answer()


@router.message(F.text == "📞 Связаться с разработчиком")
async def contact_dev(message: Message):
    await message.answer(
        f"Можно написать разработчику напрямую: @{config.developer_username}\n\n"
        "Но лучше оставьте заявку здесь — я передам все данные автоматически.",
        reply_markup=main_menu(),
    )


@router.message(F.text == "📝 Заполнить вручную")
@router.message(F.text == "📝 Оформить заявку")
async def lead_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отлично 👍 Оформим заявку.\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
        "Как вас зовут?"
    )
    await state.set_state(Lead.name)


@router.message(Lead.name)
async def lead_name(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона или Telegram для связи:")
    await state.set_state(Lead.phone)


@router.message(Lead.phone)
async def lead_phone(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(phone=message.text)
    await message.answer("Для какого бизнеса нужен бот?", reply_markup=business_kb())
    await state.set_state(Lead.business)


@router.message(Lead.business)
async def lead_business(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(business=message.text)
    await message.answer("Какой бот нужен?", reply_markup=purpose_kb())
    await state.set_state(Lead.bot_type)


@router.message(Lead.bot_type)
async def lead_bot_type(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(bot_type=message.text)
    await message.answer("Какие функции, пожелания и комментарии по боту?", reply_markup=functions_kb())
    await state.set_state(Lead.functions)


@router.message(Lead.functions)
async def lead_functions(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(functions=message.text)
    await message.answer("Нужна ли оплата в боте?", reply_markup=yes_no_kb())
    await state.set_state(Lead.payments)


@router.message(Lead.payments)
async def lead_payments(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(payments=message.text)
    await message.answer("Нужен AI-консультант?", reply_markup=yes_no_kb())
    await state.set_state(Lead.ai_needed)


@router.message(Lead.ai_needed)
async def lead_ai(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(ai_needed=message.text)
    await message.answer("По срокам как удобнее?", reply_markup=urgency_kb())
    await state.set_state(Lead.urgency)


@router.message(Lead.urgency)
async def lead_urgency(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(urgency=message.text)
    await message.answer("Добавьте пожелания или комментарии. Если нечего добавить — напишите «нет».")
    await state.set_state(Lead.comment)


@router.message(Lead.comment)
async def lead_comment(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await state.update_data(comment=message.text)
    data = await state.get_data()
    estimated = "Начнём с 1000 грн. Финальная стоимость зависит от задач и будет согласована с разработчиком."
    await message.answer(lead_summary(data, estimated), reply_markup=confirm_kb())
    await state.set_state(Lead.confirm)


@router.message(Lead.confirm, F.text == "✅ Отправить заявку")
@router.message(F.text == "✅ Отправить заявку")
async def lead_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    has_ai = bool((data.get("ai_command_text") or "").strip())
    has_form = any((data.get(k) or "").strip() for k in ["name","phone","business","bot_type","functions","payments","ai_needed","urgency","comment"])
    if not has_ai and not has_form:
        await message.answer("Сначала опишите задачу текстом/голосом или заполните заявку вручную.", reply_markup=ai_command_kb())
        return
    await send_application(message, state, bot)


@router.message(Lead.confirm, F.text == "✏️ Заполнить заново")
async def lead_restart(message: Message, state: FSMContext):
    await lead_start(message, state)


@router.message(Lead.confirm, F.text == "❌ Отменить")
async def lead_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заявка отменена. Можете вернуться в меню.", reply_markup=main_menu())


@router.message(Lead.confirm)
async def lead_confirm_any_text(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    await message.answer(
        "Скажите «отправить заявку», «заполнить заново», «отмена» или «меню».",
        reply_markup=confirm_kb(),
    )


async def execute_assistant_command(message: Message, state: FSMContext, bot: Bot, text: str) -> bool:
    is_admin = message.from_user.id in config.admin_ids
    cmd = detect_command(text, is_admin=is_admin)
    intent = cmd.get("intent")

    if intent in {"open_menu", "cancel"}:
        await state.clear()
        await message.answer("Главное меню 👇", reply_markup=main_menu())
        return True
    if intent == "admin_forbidden":
        await message.answer("Этот раздел доступен только администратору.", reply_markup=main_menu())
        return True
    if intent == "contact_developer":
        await contact_dev(message)
        return True
    if intent == "restart_lead":
        await lead_start(message, state)
        return True
    if intent == "confirm_send":
        await lead_send(message, state, bot)
        return True
    if intent == "open_examples":
        await examples(message)
        return True
    if intent == "find_example":
        found = search_examples(cmd.get("query") or text, limit=3)
        if not found:
            await message.answer("Точного примера не нашёл. Покажу доступные варианты.")
            await examples(message)
        else:
            last_title = None
            for i, ex in enumerate(found, 1):
                await message.answer(format_example(ex, i), parse_mode="HTML")
                last_title = ex.get("title")
            if last_title:
                await state.update_data(last_example_title=last_title)
            await message.answer(
                "Хотите похожий бот? Можете сказать «хочу такой бот» или нажать кнопку.",
                reply_markup=quick_lead_kb(),
            )
        return True
    if intent == "start_lead":
        await lead_start(message, state)
        return True
    if intent == "start_ai_consultant":
        await choose_ai_persona(message, state)
        return True
    if intent in {"pick_business_solution", "add_details"}:
        await state.update_data(ai_command_mode=True)
        await message.answer("Пришлите дополнительные детали голосом или текстом — я добавлю их к текущему описанию.", reply_markup=ai_command_kb())
        return True
    if intent == "open_admin" and is_admin:
        await message.answer("Админ-панель открыта.", reply_markup=admin_menu())
        return True
    if intent == "export_applications" and is_admin:
        file_path = await export_applications_csv()
        await message.answer_document(FSInputFile(file_path), caption="📥 Выгрузка заявок")
        return True
    if intent == "export_visitors" and is_admin:
        file_path = await export_visitors_csv()
        await message.answer_document(FSInputFile(file_path), caption="📥 Выгрузка посетителей бота")
        return True
    if intent == "show_applications" and is_admin:
        rows = await get_recent_applications(10)
        if not rows:
            await message.answer("Заявок пока нет.", reply_markup=admin_menu())
            return True
        lines = ["🆕 Последние заявки:"]
        for app_id, name, phone, business, bot_type, status, created_at in rows[:10]:
            lines.append(
                f"\n№{app_id}\n"
                f"Дата: {created_at}\n"
                f"Имя: {name}\n"
                f"Телефон: {phone}\n"
                f"Бизнес: {business}\n"
                f"Тип: {bot_type}\n"
                f"Статус: {status}\n\n---"
            )
        await message.answer("\n".join(lines), reply_markup=admin_menu())
        return True
    if intent == "show_stats" and is_admin:
        s = await stats()
        await message.answer(
            "📊 Статистика:\n\n"
            f"👥 Посетителей: {s.get('visitors', 0)}\n"
            f"Клиентов: {s['clients']}\n"
            f"Заявок: {s['apps']}\n"
            f"Срочных заявок: {s['urgent']}\n"
            f"Заявок с AI: {s['ai']}",
            reply_markup=admin_menu(),
        )
        return True
    if intent == "show_visitors" and is_admin:
        s = await visitor_stats()
        rows = await get_recent_visitors(10)
        text_out = (
            "👥 Посетители бота:\n\n"
            f"Всего посетителей: {s['total']}\n"
            f"Новых сегодня: {s['today']}\n"
            f"Всего запусков /start: {s['visits_total']}\n\n"
            "Последние 10 посетителей:\n\n"
        )
        if not rows:
            text_out += "Пока нет посетителей."
        else:
            for user_id, username, first_name, last_name, source, first_seen, last_seen, visits_count in rows:
                username_text = f"@{username}" if username else "без username"
                name_text = f"{first_name} {last_name}".strip() or "без имени"
                text_out += (
                    f"ID: {user_id}\nИмя: {name_text}\nUsername: {username_text}\n"
                    f"Визитов: {visits_count}\nПервый вход: {first_seen}\nПоследний вход: {last_seen}\n\n"
                )
        await message.answer(text_out, reply_markup=admin_menu())
        return True
    if intent == "create_quick_lead":
        data = await state.get_data()
        if "хочу такой бот" in (text or "").lower() and data.get("last_example_title"):
            quick = parse_quick_lead(text, message.from_user.username)
            quick["bot_type"] = data.get("last_example_title")
        else:
            quick = parse_quick_lead(text, message.from_user.username)
        old = (data.get("ai_command_text") or "").strip()
        merged = f"{old}\n{text}".strip() if old else (text or "")
        await state.update_data(ai_command_mode=True, ai_command_text=merged, **quick)
        await message.answer(
            build_quick_lead_preview(quick) + "\n\nМожете сказать голосом:\n— отправить заявку\n— дополнить\n— заполнить вручную\n— меню",
            reply_markup=ai_command_kb(),
        )
        return True
    if intent == "general_assistant":
        answer = await ai_answer(text + AI_SALES_RULES)
        await message.answer(f"{answer}\n\nЕсли хотите, могу сразу оформить заявку.", reply_markup=ai_command_kb())
        return True
    return False


async def process_fsm_voice_text(message: Message, state: FSMContext, text: str, bot: Bot) -> bool:
    cur = await state.get_state()
    if not cur:
        return False

    if cur == Lead.name.state:
        await state.update_data(name=text)
        await state.set_state(Lead.phone)
        await message.answer("Введите номер телефона или Telegram для связи:")
        return True
    if cur == Lead.phone.state:
        await state.update_data(phone=text)
        await state.set_state(Lead.business)
        await message.answer("Для какого бизнеса нужен бот?", reply_markup=business_kb())
        return True
    if cur == Lead.business.state:
        await state.update_data(business=text)
        await state.set_state(Lead.bot_type)
        await message.answer("Какой бот нужен?", reply_markup=purpose_kb())
        return True
    if cur == Lead.bot_type.state:
        await state.update_data(bot_type=text)
        await state.set_state(Lead.functions)
        await message.answer("Какие функции, пожелания и комментарии по боту?", reply_markup=functions_kb())
        return True
    if cur == Lead.functions.state:
        await state.update_data(functions=text)
        await state.set_state(Lead.payments)
        await message.answer("Нужна ли оплата в боте?", reply_markup=yes_no_kb())
        return True
    if cur == Lead.payments.state:
        await state.update_data(payments=text)
        await state.set_state(Lead.ai_needed)
        await message.answer("Нужен AI-консультант?", reply_markup=yes_no_kb())
        return True
    if cur == Lead.ai_needed.state:
        await state.update_data(ai_needed=text)
        await state.set_state(Lead.urgency)
        await message.answer("По срокам как удобнее?", reply_markup=urgency_kb())
        return True
    if cur == Lead.urgency.state:
        await state.update_data(urgency=text)
        await state.set_state(Lead.comment)
        await message.answer("Добавьте пожелания или комментарии. Если нечего добавить — напишите «нет».")
        return True
    if cur == Lead.comment.state:
        await state.update_data(comment=text)
        data = await state.get_data()
        estimated = "Начнём с 1000 грн. Финальная стоимость зависит от задач и будет согласована с разработчиком."
        await message.answer(lead_summary(data, estimated), reply_markup=confirm_kb())
        await state.set_state(Lead.confirm)
        return True
    if cur == Lead.confirm.state:
        low = text.lower()
        if any(x in low for x in ["отправ", "да", "подтверж"]):
            await send_application(message, state, bot)
            return True
        if any(x in low for x in ["отмена", "отмен", "нет"]):
            await lead_cancel(message, state)
            return True
        await message.answer("Скажите «отправить заявку» или «отмена».", reply_markup=confirm_kb())
        return True
    if cur == Quiz.purpose.state:
        await state.update_data(purpose=text)
        await state.set_state(Quiz.functions)
        await message.answer("Какие функции нужны?\n\nМожно выбрать кнопку или написать своими словами.", reply_markup=functions_kb())
        return True
    if cur == Quiz.functions.state:
        await state.update_data(functions=text)
        await state.set_state(Quiz.business)
        await message.answer("Под какой бизнес нужен бот?", reply_markup=business_kb())
        return True
    if cur == Quiz.business.state:
        await state.update_data(business=text)
        data = await state.get_data()
        await state.clear()
        await message.answer(
            f"Отлично 👍\n\nЗадача: {data.get('purpose')}\n"
            f"Функции/пожелания: {data.get('functions')}\n"
            f"Бизнес: {data.get('business')}\n\n"
            "Начнём с 1000 грн.\n"
            "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
            "Чтобы перейти дальше — нажмите кнопку «Оформить заявку».",
            reply_markup=after_quiz_kb(),
        )
        return True

    return False


@router.message(F.voice | F.audio)
async def voice_handler(message: Message, state: FSMContext, bot: Bot):
    text, err = await transcribe_voice(bot, message)
    if err:
        return await message.answer(err)

    await message.answer(f"Распознал: {text}")
    if await execute_assistant_command(message, state, bot, text):
        return
    if await process_fsm_voice_text(message, state, text, bot):
        return

    await state.update_data(last_voice_text=text)
    await process_free_text(message, state, text)


async def process_free_text(message: Message, state: FSMContext, text: str):
    data = await state.get_data()

    if data.get("ai_chat_active"):
        persona = data.get("ai_persona", "default")
        try:
            answer = await ask_ai((text or "") + AI_SALES_RULES, persona=persona)
            await message.answer(answer, reply_markup=main_menu())
            return
        except Exception:
            await message.answer("AI-консультант временно не отвечает.", reply_markup=main_menu())
            return

    text = (text or "").strip()
    if data.get("ai_command_mode") or "бот" in text.lower() or "заявк" in text.lower():
        old = data.get("ai_command_text", "")
        merged = (old + "\n" + text).strip()
        await state.update_data(ai_command_mode=True, ai_command_text=merged)
        answer = await ai_answer(merged + AI_SALES_RULES)
        await message.answer(
            f"Я понял задачу 👍\n\n{answer}\n\nХотите отправить заявку разработчику?",
            reply_markup=ai_command_kb(),
        )
        return

    answer = await ai_answer(text + AI_SALES_RULES)
    if answer:
        await message.answer(answer, reply_markup=main_menu())
    else:
        await message.answer("Выберите действие в меню 👇", reply_markup=main_menu())


async def try_global_text_command(message: Message, state: FSMContext, bot: Bot) -> bool:
    text = message.text or ""
    cmd = detect_command(text, is_admin=message.from_user.id in config.admin_ids)
    if cmd["intent"] in {
        "open_menu", "cancel", "confirm_send", "restart_lead",
        "contact_developer", "admin_forbidden",
        "open_admin", "export_applications", "export_visitors",
        "show_stats", "show_visitors", "show_applications"
    }:
        return await execute_assistant_command(message, state, bot, text)
    return False


@router.message(F.text)
async def free_ai_chat_or_fallback(message: Message, state: FSMContext, bot: Bot):
    if await try_global_text_command(message, state, bot):
        return
    if await execute_assistant_command(message, state, bot, message.text or ""):
        return
    await process_free_text(message, state, message.text or "")
