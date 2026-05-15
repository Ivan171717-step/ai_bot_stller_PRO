def analyze_internal_complexity(data: dict | str) -> dict:
    text = data if isinstance(data, str) else " ".join(str(v) for v in data.values())
    t = text.lower()
    simple = ["заявк", "меню", "кнопк", "уведомления админу", "простая форма", "запись без интеграций"]
    medium = ["ai", "google sheets", "crm", "оплат", "каталог", "корзин", "рассыл", "olx", "email", "роли админа"]
    hard = ["webapp", "парс", "мониторинг цен", "маркетплейс", "ebay", "vinted", "prom", "rozetka", "api", "личный кабинет", "аналитика", "память", "прокси", "real-time", "изображ"]
    score = {"simple": sum(1 for k in simple if k in t), "medium": sum(1 for k in medium if k in t), "hard": sum(1 for k in hard if k in t)}
    complexity = max(score, key=score.get)
    if score[complexity] == 0:
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
