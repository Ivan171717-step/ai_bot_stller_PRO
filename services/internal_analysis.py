def analyze_internal_complexity(data: dict | str) -> dict:
    text = data if isinstance(data, str) else " ".join(str(v) for v in data.values())
    t = text.lower()
    simple = ["заявк", "меню", "кнопк", "уведомления админу", "простая форма", "запись без интеграций"]
    medium = ["ai", "google sheets", "crm", "оплат", "каталог", "корзин", "рассыл", "olx", "email", "роли админа"]
    hard = ["webapp", "парс", "мониторинг цен", "маркетплейс", "ebay", "vinted", "prom", "rozetka", "api", "личный кабинет", "аналитика", "память", "прокси", "real-time", "изображ"]
    if any(k in t for k in hard):
        complexity = "hard"
    elif any(k in t for k in medium):
        complexity = "medium"
    else:
        complexity = "simple"
    questions = []
    if complexity == "hard":
        questions = [
            "какие площадки подключать?",
            "есть ли официальный API?",
            "нужна ли авторизация?",
            "как часто обновлять данные?",
            "нужны ли прокси?",
            "какие данные сохранять?",
        ]
    return {
        "complexity": complexity,
        "admin_note": f"Обнаружены признаки {complexity} проекта по ключевым словам.",
        "price_comment": "Ориентир: оценить объем после уточнений.",
        "questions": questions,
    }
