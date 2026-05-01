import re
from database import get_all_settings


def _to_int(value: str, default: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


async def price_text() -> str:
    s = await get_all_settings()
    start = _to_int(s.get("min_price"), 1000)
    max_price = _to_int(s.get("max_price"), 4500)
    deadline = s.get("deadline", "1–2 дня")
    payment_terms = s.get("payment_terms", "Оплата по факту выполнения после согласования, тестирования и передачи бота.")
    return (
        f"💰 Стоимость: СТАРТ от {start} грн\n"
        f"⏱ Ориентировочный срок: {deadline}\n\n"
        f"Каждая дополнительная задача может добавлять примерно 500–700 грн, "
        f"но предварительный расчет не превышает {max_price} грн.\n\n"
        f"✅ {payment_terms}\n\n"
        "Финальная стоимость согласовывается уже с разработчиком после уточнения всех задач."
    )


async def estimated_price(data: dict | None = None) -> str:
    data = data or {}
    s = await get_all_settings()
    start = _to_int(s.get("min_price"), 1000)
    max_price = _to_int(s.get("max_price"), 4500)
    urgent = _to_int(s.get("urgent_price"), 1000)

    functions_text = " ".join([
        str(data.get("functions", "")),
        str(data.get("bot_type", "")),
        str(data.get("payments", "")),
        str(data.get("ai_needed", "")),
        str(data.get("comment", "")),
    ]).lower()

    task_keywords = [
        "crm", "таблиц", "оплат", "ai", "ии", "каталог", "расчет", "расчёт",
        "фото", "геолока", "уведом", "запись", "корзин", "админ", "рассыл"
    ]
    task_count = sum(1 for word in task_keywords if word in functions_text)
    if task_count == 0 and functions_text.strip():
        task_count = 1

    add_min = task_count * 500
    add_max = task_count * 700

    if "сроч" in str(data.get("urgency", "")).lower():
        add_min += urgent
        add_max += urgent

    low = min(start + add_min, max_price)
    high = min(start + add_max, max_price)
    if low > high:
        low = high

    if low == high:
        price_range = f"около {high} грн"
    else:
        price_range = f"примерно {low}–{high} грн"

    return (
        f"СТАРТ от {start} грн; по вашим задачам {price_range}. "
        f"Предел предварительного расчета — до {max_price} грн. "
        "Окончательная стоимость согласовывается с разработчиком."
    )
