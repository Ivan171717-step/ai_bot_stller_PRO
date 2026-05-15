import re


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = text.replace("ё", "е")
    text = re.sub(r"[^\w\s@+\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_query(text: str) -> str:
    normalized = normalize_text(text)
    patterns = [
        r"(?:пример|бот|решение)\s+(?:для|под)\s+(.+)$",
        r"(?:покажи|есть|хочу)\s+(.+)$",
    ]
    for p in patterns:
        m = re.search(p, normalized)
        if m:
            return m.group(1).strip(" ?!.,")
    for token in ["магазин", "доставка", "салон", "webapp", "ai", "сложн"]:
        if token in normalized:
            return token
    return ""


def looks_like_lead_request(text: str) -> bool:
    t = normalize_text(text)
    return any(x in t for x in ["нужен бот", "хочу бот", "сделайте бота", "бот для", "оформить заявку"])


def looks_like_question(text: str) -> bool:
    t = normalize_text(text)
    return "?" in (text or "") or any(t.startswith(x) for x in ["что", "какой", "зачем", "как"])


def detect_command(text: str, is_admin: bool = False) -> dict:
    raw = text or ""
    t = normalize_text(raw)
    query = extract_query(raw)

    def out(intent: str, confidence: float = 0.9):
        return {"intent": intent, "confidence": confidence, "query": query, "raw_text": raw}

    if any(x in t for x in ["вернись в меню", "главное меню", "в меню", "назад", "меню"]):
        return out("open_menu")
    if any(x in t for x in ["отмена", "отменить"]):
        return out("cancel")
    if any(x in t for x in ["отправить заявку", "подтверждаю", "да отправить", "покажи заявки"]):
        return out("confirm_send")
    if any(x in t for x in ["заполнить заново", "начать заново"]):
        return out("restart_lead")
    if any(x in t for x in ["связаться с разработчиком", "контакт разработчика", "написать разработчику"]):
        return out("contact_developer")

    if any(x in t for x in ["открой примеры", "покажи примеры", "какие боты можно сделать", "примеры ботов"]):
        return out("open_examples")
    if any(x in t for x in ["покажи пример", "пример для", "бот для", "покажи webapp", "сложные боты", "ботов с ai"]):
        return out("find_example", 0.85)
    if any(x in t for x in ["оформить заявку", "хочу оставить заявку", "создать заявку"]):
        return out("start_lead")
    if any(x in t for x in ["ai консультант", "открой ai", "включи консультанта", "поговорить с ai"]):
        return out("start_ai_consultant")
    if any(x in t for x in ["подбери решение", "под мой бизнес", "какой бот подойдет"]):
        return out("pick_business_solution")
    if any(x in t for x in ["добавить детали", "дополнить"]):
        return out("add_details")

    if is_admin and any(x in t for x in ["админка", "покажи админку", "открой админку"]):
        return out("open_admin")
    if is_admin and any(x in t for x in ["выгрузи заявки", "экспорт заявок"]):
        return out("export_applications")
    if is_admin and any(x in t for x in ["выгрузи клиентов", "экспорт посетителей"]):
        return out("export_visitors")
    if is_admin and any(x in t for x in ["статистика", "покажи статистику"]):
        return out("show_stats")
    if is_admin and any(x in t for x in ["посетители", "кто заходил"]):
        return out("show_visitors")

    if looks_like_lead_request(raw):
        return out("create_quick_lead", 0.8)
    if looks_like_question(raw):
        return out("general_assistant", 0.7)
    return out("unknown", 0.2)
