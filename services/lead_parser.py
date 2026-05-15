import re


def parse_quick_lead(text: str, username: str | None = None) -> dict:
    t = (text or "").lower()
    business = "Не указано"
    if "магазин" in t:
        business = "магазин одежды" if "одежд" in t else "магазин"
    elif "салон" in t:
        business = "салон красоты"
    elif "достав" in t:
        business = "доставка суши" if "суш" in t else "доставка"

    if "достав" in t:
        bot_type = "бот доставки"
    elif "запис" in t or "салон" in t:
        bot_type = "бот для записи"
    elif "магазин" in t:
        bot_type = "бот-магазин"
    else:
        bot_type = "Не указано"

    funcs = [k for k in ["каталог", "заявки", "меню", "оформление заказов", "запись клиентов", "оплата"] if k in t]
    functions = ", ".join(funcs) if funcs else (text or "")
    payments = "Да" if "оплат" in t else "Нет"
    ai_needed = "Да" if (" ai" in f" {t}" or "ии" in t or "консультант" in t) else "Нет"
    urgency = "Очень срочно" if "сроч" in t else "Обычный срок"

    phone_match = re.search(r"(\+?\d[\d\s\-\(\)]{8,}\d)", text or "")
    nick_match = re.search(r"@\w+", text or "")
    contact = nick_match.group(0) if nick_match else (phone_match.group(1) if phone_match else (f"@{username}" if username else "Не указано"))

    return {
        "business": business,
        "bot_type": bot_type,
        "functions": functions,
        "payments": payments,
        "ai_needed": ai_needed,
        "urgency": urgency,
        "phone": contact,
        "comment": text or "",
    }


def build_quick_lead_preview(data: dict) -> str:
    return (
        "Черновик заявки 📝\n\n"
        f"Бизнес: {data.get('business', 'Не указано')}\n"
        f"Тип бота: {data.get('bot_type', 'Не указано')}\n"
        f"Функции: {data.get('functions', 'Не указано')}\n"
        f"Оплата: {data.get('payments', 'Не указано')}\n"
        f"AI-консультант: {data.get('ai_needed', 'Не указано')}\n"
        f"Срочность: {data.get('urgency', 'Обычный срок')}\n"
        f"Контакт: {data.get('phone', 'Не указано')}\n\n"
        "Начнём с 1000 грн.\n"
        "Финальная стоимость зависит от задач и будет согласована с разработчиком"
    )
