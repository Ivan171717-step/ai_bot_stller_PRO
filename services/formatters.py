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
        f"Предварительная стоимость: {estimated}\n\n"
        "Оплата по факту выполнения: после согласования, тестирования и передачи бота. Окончательная стоимость согласовывается с разработчиком."
    )

def admin_lead_text(app_id: int, user, data: dict, estimated: str) -> str:
    username = f"@{user.username}" if user.username else "не указан"
    return (
        f"🆕 Новая заявка №{app_id} на Telegram-бота\n\n"
        f"Клиент: {data.get('name','-')}\n"
        f"Телефон: {data.get('phone','-')}\n"
        f"Telegram: {username}\n"
        f"User ID: {user.id}\n\n"
        f"Бизнес: {data.get('business','-')}\n"
        f"Тип бота: {data.get('bot_type','-')}\n"
        f"Функции: {data.get('functions','-')}\n"
        f"Платежи: {data.get('payments','-')}\n"
        f"AI: {data.get('ai_needed','-')}\n"
        f"Срочность: {data.get('urgency','-')}\n"
        f"Комментарий: {data.get('comment','-')}\n"
        f"Предварительная стоимость: {estimated}\n"
        "Статус: новая"
    )
