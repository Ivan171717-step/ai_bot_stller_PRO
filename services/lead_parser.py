import re


def parse_quick_lead(text: str, username: str | None = None) -> dict:
    t = (text or "").lower()
    business = "Не указано"
    if "сто" in t or "автосервис" in t:
        business = "автосервис / СТО"
    elif "недвиж" in t:
        business = "недвижимость"
    elif "курс" in t or "обучен" in t:
        business = "курсы / обучение"
    elif "часы" in t:
        business = "магазин часов"
    elif "olx" in t:
        business = "OLX"
    elif "маркетплейс" in t:
        business = "маркетплейс"
    elif "webapp" in t:
        business = "WebApp"
    elif "crm" in t:
        business = "CRM"
    elif "faq" in t or "поддержк" in t:
        business = "поддержка / FAQ"
    elif "кафе" in t or "ресторан" in t or "суш" in t or "доставка еды" in t:
        business = "кафе / ресторан / доставка еды"
    elif "металлолом" in t:
        business = "металлолом"
    elif "магазин" in t:
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

    func_map = {
        "парсинг": ["парсинг", "парсер", "парс"],
        "мониторинг цен": ["мониторинг цен", "цены", "price monitoring"],
        "WebApp": ["webapp"],
        "CRM": ["crm"],
        "Google Sheets": ["google sheets", "гугл таблиц", "таблиц"],
        "уведомления": ["уведомлен"],
        "рассылка": ["рассыл"],
        "корзина": ["корзин"],
        "запись": ["запис"],
        "геолокация": ["геолокац"],
        "фото": ["фото", "изображ"],
        "AI-память": ["ai-памят", "ai память", "память"],
        "каталог": ["каталог"],
        "заявки": ["заявк"],
        "меню": ["меню"],
        "оформление заказов": ["оформление заказов", "заказ"],
    }
    funcs = [name for name, keys in func_map.items() if any(k in t for k in keys)]
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
