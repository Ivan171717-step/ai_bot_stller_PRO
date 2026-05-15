from openai import AsyncOpenAI

from config import config
from services.personas import PERSONAS


SYSTEM_FALLBACK = (
    "Ты AI-консультант по созданию Telegram-ботов для бизнеса. "
    "Общайся дружелюбно, коротко и по делу. "
    "Помогай понять бизнес, предложить тип бота, выгоды и мягко вести к заявке. "
    "Стоимость: СТАРТ от 1000 грн. "
    "Дополнительные задачи добавляют примерно 500–700 грн, но предварительный расчет не выше 4500 грн. "
    "Финальная стоимость согласовывается с разработчиком. "
    "Оплата по факту выполнения, тестирования и передачи клиенту."
)


def get_openai_key() -> str | None:
    """
    Берем ключ из объекта config.
    Поддерживает разные варианты названия поля.
    """
    return (
        getattr(config, "openai_api_key", None)
        or getattr(config, "OPENAI_API_KEY", None)
        or getattr(config, "api_key", None)
    )


OPENAI_API_KEY = get_openai_key()
client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def ask_ai(user_text: str, persona: str = "default") -> str:
    if not user_text or not user_text.strip():
        return (
            "Напишите, для какого бизнеса нужен бот, "
            "а я помогу подобрать подходящий вариант 👍"
        )

    if (not config.use_ai) or client is None:
        return (
            "AI-консультант пока не подключен: не найден OPENAI_API_KEY.\n\n"
            "Проверьте файл .env и config.py.\n"
            "Но заявку можно оформить через кнопку 📝 Оформить заявку."
        )

    selected_persona = PERSONAS.get(persona, PERSONAS.get("default"))

    system_prompt = (
        selected_persona.get("prompt")
        if isinstance(selected_persona, dict) and selected_persona.get("prompt")
        else SYSTEM_FALLBACK
    )

    try:
        response = await client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_text.strip(),
                },
            ],
            temperature=0.85,
            max_tokens=600,
        )

        answer = response.choices[0].message.content

        if not answer:
            return (
                "Я понял задачу 👍\n"
                "Можем подобрать структуру бота и оформить заявку."
            )

        return answer.strip()

    except Exception as error:
        print(f"OpenAI error: {error}")
        return (
            "AI-консультант временно не отвечает.\n\n"
            "Можно продолжить через кнопку 📝 Оформить заявку, "
            "и разработчик согласует детали напрямую."
        )


async def ai_answer(user_text: str) -> str:
    return await ask_ai(user_text, persona="default")