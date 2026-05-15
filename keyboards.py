from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤖 Какой вам нужен бот")],
            [KeyboardButton(text="🧠 AI-консультант"), KeyboardButton(text="🎙 AI-команда")],
            [KeyboardButton(text="🏢 Под какой бизнес")],
            [KeyboardButton(text="🎯 Подобрать решение под мой бизнес")],
            [KeyboardButton(text="🎨 Примеры ботов")],
            [KeyboardButton(text="📝 Оформить заявку")],
            [KeyboardButton(text="📞 Связаться с разработчиком")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел 👇"
    )


def persona_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌸 Анастейша — мягко и с легким флиртом",
                    callback_data="persona:anastasia"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧔 Джейсон — жестко и по делу",
                    callback_data="persona:jason"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Стандартный консультант",
                    callback_data="persona:default"
                )
            ],
        ]
    )


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Новые заявки"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="👥 Посетители"), KeyboardButton(text="📥 Выгрузка клиентов")],
            [KeyboardButton(text="📥 Выгрузка заявок")],
            [KeyboardButton(text="💰 Настроить цены"), KeyboardButton(text="📦 Пакеты")],
            [KeyboardButton(text="🎨 Примеры"), KeyboardButton(text="⚙️ Настройки")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )


def purpose_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Прием заявок"), KeyboardButton(text="Продажи")],
            [KeyboardButton(text="Каталог товаров"), KeyboardButton(text="Запись клиентов")],
            [KeyboardButton(text="Поддержка клиентов"), KeyboardButton(text="AI-консультант")],
            [KeyboardButton(text="Автоматизация бизнеса"), KeyboardButton(text="Другое")],
        ],
        resize_keyboard=True
    )


def functions_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кнопки и меню"), KeyboardButton(text="Прием заявок")],
            [KeyboardButton(text="CRM / таблица"), KeyboardButton(text="Уведомления админу")],
            [KeyboardButton(text="Оплата"), KeyboardButton(text="AI-ответы")],
            [KeyboardButton(text="Каталог"), KeyboardButton(text="Расчет стоимости")],
            [KeyboardButton(text="Фото"), KeyboardButton(text="Геолокация")],
            [KeyboardButton(text="Готово")],
        ],
        resize_keyboard=True
    )


def business_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Услуги"), KeyboardButton(text="Интернет-магазин")],
            [KeyboardButton(text="Доставка"), KeyboardButton(text="Обучение")],
            [KeyboardButton(text="Салон / запись"), KeyboardButton(text="Металлолом")],
            [KeyboardButton(text="Недвижимость"), KeyboardButton(text="Авто")],
            [KeyboardButton(text="Другое")],
        ],
        resize_keyboard=True
    )


def yes_no_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
        resize_keyboard=True
    )


def urgency_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обычный срок")],
            [KeyboardButton(text="Очень срочно")],
        ],
        resize_keyboard=True
    )


def after_quiz_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Оформить заявку")],
            [KeyboardButton(text="🎨 Примеры ботов")],
            [KeyboardButton(text="📞 Связаться с разработчиком")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )


def confirm_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Отправить заявку")],
            [KeyboardButton(text="✏️ Заполнить заново"), KeyboardButton(text="❌ Отменить")],
        ],
        resize_keyboard=True
    )


def examples_inline(examples) -> InlineKeyboardMarkup:
    buttons = []
    for ex_id, title, _desc in examples:
        buttons.append([
            InlineKeyboardButton(
                text=f"Хочу такой: {title}",
                callback_data=f"want_example:{ex_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_application_kb(app_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Взять в работу", callback_data=f"status:{app_id}:в работе")],
            [InlineKeyboardButton(text="Согласование", callback_data=f"status:{app_id}:согласование")],
            [InlineKeyboardButton(text="Тестирование", callback_data=f"status:{app_id}:тестирование")],
            [InlineKeyboardButton(text="Выполнена", callback_data=f"status:{app_id}:выполнена")],
            [InlineKeyboardButton(text="Отменена", callback_data=f"status:{app_id}:отменена")],
        ]
    )


def ai_command_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Отправить заявку")],
            [KeyboardButton(text="🎙 Добавить детали голосом")],
            [KeyboardButton(text="📝 Заполнить вручную")],
            [KeyboardButton(text="📞 Связаться с разработчиком")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )


def quick_lead_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Отправить заявку")],
            [KeyboardButton(text="📝 Заполнить вручную")],
            [KeyboardButton(text="📞 Связаться с разработчиком")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )
