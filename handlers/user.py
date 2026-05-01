from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from config import config
from states import Quiz, Lead
from keyboards import (
    main_menu,
    persona_keyboard,
    purpose_kb,
    functions_kb,
    business_kb,
    yes_no_kb,
    urgency_kb,
    confirm_kb,
    examples_inline,
    after_quiz_kb,
)
from database import get_examples, save_application
from services.pricing import estimated_price
from services.formatters import lead_summary, admin_lead_text
from services.ai_service import ai_answer, ask_ai
from services.google_sheets import send_to_sheets

router = Router()

WELCOME = (
    "Здравствуйте 👋\n\n"
    "Я AI-консультант по созданию Telegram-ботов для бизнеса.\n"
    "Помогу понять, какой бот подойдет именно вам, примерно оценить бюджет и оформить заявку.\n\n"
    "Начнём с 1000 грн.\n"
    "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
    "Выберите действие ниже 👇"
)


AI_SALES_RULES = (
    "\n\nПравила ответа:\n"
    "1. Веди диалог как AI-консультант по разработке Telegram-ботов.\n"
    "2. Мягко веди клиента к конкретному следующему действию.\n"
    "3. Если нужно перейти к разделу, попроси клиента самостоятельно нажать нужную кнопку.\n"
    "4. Не говори, что ты сам нажал кнопку.\n"
    "5. Используй фразу: «Начнём с 1000 грн».\n"
    "6. Не указывай стоимость дополнительных функций.\n"
    "7. Пиши, что финальная стоимость зависит от задач и согласовывается с разработчиком.\n"
    "8. Если клиент сомневается, предложи начать с простой заявки.\n"
    "9. Предлагай кнопки: «Какой вам нужен бот», «Оформить заявку», «Связаться с разработчиком».\n"
)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    # Записываем посетителя в Google Sheets после /start
    send_to_sheets("visitor", {
        "user_id": message.from_user.id,
        "username": message.from_user.username or "",
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
        "source": "telegram"
    })

    banner = "assets/banner.png"
    try:
        await message.answer_photo(
            FSInputFile(banner),
            caption=WELCOME,
            reply_markup=main_menu()
        )
    except Exception:
        await message.answer(WELCOME, reply_markup=main_menu())


@router.message(F.text == "⬅️ В меню")
async def menu_back(message: Message, state: FSMContext):
    await state.update_data(ai_chat_active=False)
    await message.answer("Главное меню 👇", reply_markup=main_menu())


@router.message(F.text == "🤖 Какой вам нужен бот")
async def quiz_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Давайте быстро поймем задачу.\n\n"
        "Для чего вам нужен бот?",
        reply_markup=purpose_kb()
    )
    await state.set_state(Quiz.purpose)


@router.message(Quiz.purpose)
async def quiz_purpose(message: Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    await message.answer(
        "Какие функции нужны?\n\n"
        "Можно выбрать кнопку или написать своими словами.",
        reply_markup=functions_kb()
    )
    await state.set_state(Quiz.functions)


@router.message(Quiz.functions)
async def quiz_functions(message: Message, state: FSMContext):
    await state.update_data(functions=message.text)
    await message.answer(
        "Под какой бизнес нужен бот?",
        reply_markup=business_kb()
    )
    await state.set_state(Quiz.business)


@router.message(Quiz.business)
async def quiz_business(message: Message, state: FSMContext):
    await state.update_data(business=message.text)
    data = await state.get_data()

    await state.clear()

    await message.answer(
        "Отлично 👍\n\n"
        f"Задача: {data.get('purpose')}\n"
        f"Функции/пожелания: {data.get('functions')}\n"
        f"Бизнес: {data.get('business')}\n\n"
        "💰 Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
        "Ваш бот может быть похож на этот — и даже намного лучше: "
        "с вашими кнопками, заявками, CRM, AI-консультантом и нужной логикой.\n\n"
        "Чтобы перейти дальше — нажмите кнопку «Оформить заявку».",
        reply_markup=after_quiz_kb()
    )


@router.message(F.text == "🧠 AI-консультант")
async def choose_ai_persona(message: Message, state: FSMContext):
    await state.update_data(ai_chat_active=False)
    await message.answer(
        "Выберите стиль AI-консультанта 👇\n\n"
        "🌸 Анастейша — мягко, дружелюбно и понятно\n"
        "🧔 Джейсон — уверенно, по делу и с лёгким юмором\n"
        "🤖 Стандартный — спокойно и нейтрально",
        reply_markup=persona_keyboard()
    )


@router.callback_query(F.data.startswith("persona:"))
async def set_persona(callback: CallbackQuery, state: FSMContext):
    persona = callback.data.split(":")[1]
    await state.update_data(ai_persona=persona, ai_chat_active=True)

    if persona == "anastasia":
        text = (
            "🌸 Я Анастейша 😊\n\n"
            "Помогу подобрать Telegram-бота под ваш бизнес мягко и понятно.\n\n"
            "Начнём с 1000 грн.\n"
            "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
            "Расскажите, чем занимается ваш бизнес?"
        )
    elif persona == "jason":
        text = (
            "🧔 Я Джейсон.\n\n"
            "Разберем задачу быстро и без лишней воды.\n"
            "Бизнес не должен терять заявки. Бот должен их принимать.\n\n"
            "Начнём с 1000 грн.\n"
            "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
            "Какой бизнес автоматизируем?"
        )
    else:
        text = (
            "🤖 Я AI-консультант.\n\n"
            "Помогу выбрать бота, функции и оформить заявку.\n\n"
            "Начнём с 1000 грн.\n"
            "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
            "Для какого бизнеса нужен бот?"
        )

    await callback.message.answer(text, reply_markup=main_menu())
    await callback.answer()


@router.message(F.text == "🏢 Под какой бизнес")
async def business_info(message: Message):
    await message.answer(
        "Ботов можно сделать почти под любой бизнес:\n\n"
        "— услуги\n"
        "— магазины\n"
        "— доставка\n"
        "— обучение\n"
        "— запись клиентов\n"
        "— металлолом\n"
        "— недвижимость\n"
        "— авто\n\n"
        "Главное — понять, какие действия бот должен выполнять вместо менеджера: "
        "принимать заявки, считать примерную стоимость, показывать каталог, "
        "записывать клиентов или консультировать.\n\n"
        "Чтобы я задал несколько вопросов — нажмите кнопку «Какой вам нужен бот».\n"
        "Если уже готовы — нажмите «Оформить заявку».",
        reply_markup=main_menu()
    )


@router.message(F.text == "🎨 Примеры ботов")
async def examples(message: Message):
    rows = await get_examples()
    text = "🎨 Примеры демо-ботов:\n\n"

    for i, (_id, title, desc) in enumerate(rows, start=1):
        text += f"{i}. {title}\n{desc}\n\n"

    text += (
        "Ссылки в демо можно заменить в админ-панели на ваши реальные демо-боты.\n\n"
        "Ваш бот может быть похож на один из этих вариантов — или намного лучше, под ваш бизнес.\n\n"
        "Если хотите похожий вариант — нажмите «Оформить заявку»."
    )

    await message.answer(text, reply_markup=examples_inline(rows))


@router.callback_query(F.data.startswith("want_example:"))
async def want_example(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(bot_type="Хочу бот как пример")
    await callback.message.answer(
        "Отлично 👍\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
        "Как вас зовут?"
    )
    await state.set_state(Lead.name)


@router.message(F.text == "📞 Связаться с разработчиком")
async def contact_dev(message: Message):
    await message.answer(
        f"Можно написать разработчику напрямую: @{config.developer_username}\n\n"
        "Но лучше оставьте заявку здесь — я передам все данные автоматически: "
        "имя, контакт, бизнес, задачи и пожелания.\n\n"
        "Для этого нажмите кнопку «Оформить заявку».",
        reply_markup=main_menu()
    )


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
async def lead_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона или Telegram для связи:")
    await state.set_state(Lead.phone)


@router.message(Lead.phone)
async def lead_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Для какого бизнеса нужен бот?", reply_markup=business_kb())
    await state.set_state(Lead.business)


@router.message(Lead.business)
async def lead_business(message: Message, state: FSMContext):
    await state.update_data(business=message.text)
    await message.answer(
        "Какой бот нужен?\n\n"
        "Например: заявки, магазин, AI-консультант, запись клиентов, каталог, рассылки.",
        reply_markup=purpose_kb()
    )
    await state.set_state(Lead.bot_type)


@router.message(Lead.bot_type)
async def lead_bot_type(message: Message, state: FSMContext):
    await state.update_data(bot_type=message.text)
    await message.answer(
        "Какие функции, пожелания и комментарии по боту?\n\n"
        "Можно написать списком.",
        reply_markup=functions_kb()
    )
    await state.set_state(Lead.functions)


@router.message(Lead.functions)
async def lead_functions(message: Message, state: FSMContext):
    await state.update_data(functions=message.text)
    await message.answer("Нужна ли оплата в боте?", reply_markup=yes_no_kb())
    await state.set_state(Lead.payments)


@router.message(Lead.payments)
async def lead_payments(message: Message, state: FSMContext):
    await state.update_data(payments=message.text)
    await message.answer("Нужен AI-консультант?", reply_markup=yes_no_kb())
    await state.set_state(Lead.ai_needed)


@router.message(Lead.ai_needed)
async def lead_ai(message: Message, state: FSMContext):
    await state.update_data(ai_needed=message.text)
    await message.answer("По срокам как удобнее?", reply_markup=urgency_kb())
    await state.set_state(Lead.urgency)


@router.message(Lead.urgency)
async def lead_urgency(message: Message, state: FSMContext):
    await state.update_data(urgency=message.text)
    await message.answer(
        "Добавьте пожелания, комментарии или детали задачи.\n\n"
        "Например: стиль общения, нужные кнопки, примеры ботов, особенности бизнеса.\n"
        "Если нечего добавить — напишите «нет»."
    )
    await state.set_state(Lead.comment)


@router.message(Lead.comment)
async def lead_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    estimated = (
        "Начнём с 1000 грн. "
        "Финальная стоимость зависит от задач и будет согласована с разработчиком."
    )

    await message.answer(lead_summary(data, estimated), reply_markup=confirm_kb())
    await state.set_state(Lead.confirm)


@router.message(Lead.confirm, F.text == "✅ Отправить заявку")
async def lead_send(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    estimated = (
        "Начнём с 1000 грн. "
        "Финальная стоимость зависит от задач и будет согласована с разработчиком."
    )

    app_id = await save_application(message.from_user, data, estimated)

    # Записываем заявку в Google Sheets
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
        "price": estimated
    })

    for admin_id in config.admin_ids:
        await bot.send_message(
            admin_id,
            admin_lead_text(app_id, message.from_user, data, estimated)
        )

    await message.answer(
        "Заявка отправлена ✅\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
        "Разработчик свяжется с вами для уточнения деталей.",
        reply_markup=main_menu()
    )
    await state.clear()


@router.message(Lead.confirm, F.text == "✏️ Заполнить заново")
async def lead_restart(message: Message, state: FSMContext):
    await lead_start(message, state)


@router.message(Lead.confirm, F.text == "❌ Отменить")
async def lead_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Заявка отменена. Можете вернуться в меню.",
        reply_markup=main_menu()
    )


@router.message(F.text)
async def free_ai_chat_or_fallback(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("ai_chat_active"):
        persona = data.get("ai_persona", "default")

        try:
            prompt = message.text + AI_SALES_RULES
            answer = await ask_ai(prompt, persona=persona)
            await message.answer(answer, reply_markup=main_menu())
            return

        except Exception:
            await message.answer(
                "AI-консультант временно не отвечает.\n\n"
                "Но вы можете нажать кнопку «Оформить заявку», и мы соберём данные для разработчика.",
                reply_markup=main_menu()
            )
            return

    answer = await ai_answer((message.text or "") + AI_SALES_RULES)

    if answer:
        await message.answer(answer, reply_markup=main_menu())
    else:
        await message.answer(
            "Я помогу подобрать Telegram-бота под ваш бизнес, примерно оценить решение и оформить заявку.\n\n"
            "Начнём с 1000 грн.\n"
            "Финальная стоимость зависит от задач и будет согласована с разработчиком.\n\n"
            "Чтобы продолжить — нажмите кнопку «Какой вам нужен бот» или «Оформить заявку».",
            reply_markup=main_menu()
        )