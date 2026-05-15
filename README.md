# AI Telegram Bot Seller

Telegram-бот на **Python + aiogram 3** для продажи услуги разработки Telegram-ботов под бизнес.

## Что добавлено
- Голосовое управление (voice/audio) на всех этапах: распознавание через Whisper и подстановка в текущий сценарий FSM.
- Кнопка **🎙 AI-команда** в главном меню.
- Уведомление админу только о **первом** входе нового посетителя.
- Раздел **🎨 Примеры ботов** теперь читает JSON из `examples/`.
- Экспорт заявок в CSV: `data/applications_export.csv`.
- Единая формулировка по цене:
  - **Начнём с 1000 грн**
  - **Финальная стоимость зависит от задач и будет согласована с разработчиком**

## Переменные окружения
См. `.env.example`:
- `BOT_TOKEN`
- `ADMIN_IDS`
- `DEVELOPER_USERNAME`
- `USE_AI`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `GOOGLE_SHEETS_ENABLED`
- `GOOGLE_SCRIPT_URL`
- `GOOGLE_SCRIPT_SECRET`
- `OLX_EMAIL_LOGIN`
- `OLX_EMAIL_PASSWORD`
- `DB_PATH`

## Как включить голос
```env
USE_AI=true
OPENAI_API_KEY=ваш_ключ
OPENAI_MODEL=gpt-4o-mini
```
Если ключ не указан, бот отвечает:
> Голосовое распознавание пока не подключено. Можно написать текстом.

## Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

## Railway
1. Подключите GitHub-репозиторий в Railway.
2. Добавьте переменные из `.env.example`.
3. Старт: `python bot.py` (или через Procfile).

## Python runtime
`runtime.txt`:
```text
python-3.11.8
```
