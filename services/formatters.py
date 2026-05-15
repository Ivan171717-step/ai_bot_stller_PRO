def lead_summary(data: dict, estimated: str) -> str:
    return (
        "📝 Проверьте заявку:\n\n"
        f"Имя: {data.get('name','-')}\n"
        f"Телефон: {data.get('phone','-')}\n"
        f"Бизнес: {data.get('business','-')}\n"
        f"Тип бота: {data.get('bot_type','-')}\n"
        f"Функции: {data.get('functions','-')}\n"
        f"Платежи: {data.get('payments','-')}\n"
        f"AI: {data.get('ai_needed','-')}\n"
        f"Срочность: {data.get('urgency','-')}\n"
        f"Комментарий: {data.get('comment','-')}\n"
        f"Предварительная стоимость: {estimated}"
    )


def internal_admin_note_text(analysis: dict) -> str:
    q = "\n".join(f"— {x}" for x in analysis.get("questions", [])) or "— Уточняющие вопросы не требуются"
    return (
        "🧠 Внутренний комментарий AI\n"
        f"Сложность: {analysis.get('complexity', 'simple').upper()}\n"
        f"Почему: {analysis.get('admin_note', '-')}\n"
        f"Ориентир для себя: {analysis.get('price_comment', '-')}\n"
        f"Что уточнить:\n{q}"
    )


def admin_lead_text(app_id: int, user, data: dict, estimated: str, internal_note: str = "") -> str:
    username = f"@{user.username}" if user.username else "не указан"
    return (
        f"🆕 Новая заявка №{app_id} на Telegram-бота\n\n"
        f"Клиент: {data.get('name','-')}\nТелефон: {data.get('phone','-')}\nTelegram: {username}\nUser ID: {user.id}\n\n"
        f"Бизнес: {data.get('business','-')}\nТип бота: {data.get('bot_type','-')}\nФункции: {data.get('functions','-')}\n"
        f"Платежи: {data.get('payments','-')}\nAI: {data.get('ai_needed','-')}\nСрочность: {data.get('urgency','-')}\nКомментарий: {data.get('comment','-')}\n"
        f"Предварительная стоимость: {estimated}\nСтатус: новая\n\n{internal_note}".strip()
    )
