# AI Telegram Bot Seller

Telegram-бот для продажи услуги разработки Telegram-ботов под бизнес.

## Возможности\n\nАктуальная логика меню:\n\n- 🤖 Какой вам нужен бот\n- 🧠 AI-консультант\n- 🏢 Под какой бизнес\n- 🎨 Примеры ботов\n- 📝 Оформить заявку\n- 📞 Связаться с разработчиком\n

- красивый стартовый баннер;
- AI-консультант, если включить OpenAI API;
- меню кнопками;
- квиз “какой бот вам нужен”; 
- мягкий расчет: СТАРТ от 1000 грн + 500–700 грн за дополнительные задачи, без превышения лимита 4500 грн;
- условия оплаты по факту выполнения;
- оформление заявки;
- сохранение клиентов и заявок в SQLite;
- отправка заявки админу;
- админ-панель `/admin`;
- изменение стартовой цены, предела расчета, срочности, сроков и условий оплаты через админку;
- пакеты услуг: Старт / Бизнес / AI;
- примеры ботов с кнопкой “Хочу такой”.

---

## Логика стоимости

По умолчанию бот показывает:

- СТАРТ от 1000 грн;
- дополнительные задачи добавляют примерно 500–700 грн;
- предварительный расчет не превышает 4500 грн;
- окончательная стоимость согласовывается с разработчиком.

Изменить эти значения можно через `/admin` → `💰 Настроить цены`.

## Демо-ссылки

В разделе `🎨 Примеры ботов` сейчас стоят примерные ссылки:

- `https://t.me/demo_request_bot`
- `https://t.me/demo_shop_bot`
- `https://t.me/demo_ai_consultant_bot`
- `https://t.me/demo_booking_bot`

После создания реальных демо-ботов замените ссылки через `/admin` → `🎨 Примеры`.


---

## 1. Как получить токен Telegram-бота

1. Откройте Telegram.
2. Найдите `@BotFather`.
3. Напишите `/newbot`.
4. Укажите название бота.
5. Укажите username бота, который заканчивается на `bot`.
6. Скопируйте токен.

---

## 2. Как узнать свой ADMIN_ID

1. Откройте Telegram.
2. Найдите `@userinfobot` или `@getmyid_bot`.
3. Нажмите Start.
4. Скопируйте свой ID.

---

## 3. Локальный запуск на Windows / PyCharm

### Шаг 1. Распакуйте проект

Распакуйте архив в удобную папку, например:

```bash
D:\ai_bot_seller
```

### Шаг 2. Откройте папку в PyCharm

File → Open → выберите папку проекта.

### Шаг 3. Создайте виртуальное окружение

В терминале PyCharm:

```bash
python -m venv .venv
```

Активируйте окружение:

```bash
.venv\Scripts\activate
```

### Шаг 4. Установите зависимости

```bash
pip install -r requirements.txt
```

### Шаг 5. Создайте `.env`

Скопируйте `.env.example` в `.env`.

Пример:

```env
BOT_TOKEN=123456:ABCDEF
ADMIN_IDS=123456789
DEVELOPER_USERNAME=your_username
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
USE_AI=false
```

Если AI пока не нужен, оставьте:

```env
USE_AI=false
```

### Шаг 6. Запустите бота

```bash
python bot.py
```

---

## 4. Как включить AI

1. Получите OpenAI API key.
2. В `.env` укажите:

```env
OPENAI_API_KEY=ваш_ключ
USE_AI=true
OPENAI_MODEL=gpt-4o-mini
```

3. Перезапустите бота.

Если AI не включен, бот все равно работает по кнопкам и сценариям.

---

## 5. Админ-панель

В Telegram напишите боту:

```text
/admin
```

В админке можно:

- смотреть заявки;
- менять статусы;
- смотреть статистику;
- менять стартовую цену, предел предварительного расчета и доплату за срочность;
- менять сроки;
- менять условия оплаты;
- добавлять пакеты;
- добавлять примеры ботов.

---

## 6. Как загрузить проект на GitHub

### Шаг 1. Создайте репозиторий

На GitHub создайте новый репозиторий, например:

```text
ai-bot-seller
```

### Шаг 2. В терминале проекта выполните

```bash
git init
git add .
git commit -m "Initial commit: AI Telegram bot seller"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-bot-seller.git
git push -u origin main
```

Важно: файл `.env` не попадет в GitHub, потому что он добавлен в `.gitignore`.

---

## 7. Деплой на Railway

1. Зайдите на Railway.
2. New Project → Deploy from GitHub repo.
3. Выберите репозиторий.
4. В Variables добавьте:

```env
BOT_TOKEN=ваш_токен
ADMIN_IDS=ваш_id
DEVELOPER_USERNAME=ваш_telegram_username
USE_AI=false
```

Если нужен AI:

```env
OPENAI_API_KEY=ваш_openai_key
USE_AI=true
OPENAI_MODEL=gpt-4o-mini
```

5. Railway сам увидит `Procfile`:

```text
worker: python bot.py
```

6. Запустите Deploy.

---

## 8. Деплой на Render

1. Создайте новый Web Service или Background Worker.
2. Подключите GitHub-репозиторий.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command:

```bash
python bot.py
```

5. Добавьте переменные окружения из `.env`.

---

## 9. Деплой на VPS

### Установка

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git -y
```

### Клонирование

```bash
git clone https://github.com/YOUR_USERNAME/ai-bot-seller.git
cd ai-bot-seller
```

### Настройка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

### Проверка запуска

```bash
python bot.py
```

### Запуск через systemd

Создайте файл:

```bash
sudo nano /etc/systemd/system/ai-bot-seller.service
```

Вставьте:

```ini
[Unit]
Description=AI Telegram Bot Seller
After=network.target

[Service]
WorkingDirectory=/root/ai-bot-seller
ExecStart=/root/ai-bot-seller/.venv/bin/python /root/ai-bot-seller/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Если проект лежит не в `/root/ai-bot-seller`, замените путь.

Запуск:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-bot-seller
sudo systemctl start ai-bot-seller
sudo systemctl status ai-bot-seller
```

Логи:

```bash
journalctl -u ai-bot-seller -f
```

---

## 10. Частые ошибки

### BOT_TOKEN is not set

Создайте `.env` и добавьте токен.

### ADMIN_IDS is not set

Добавьте свой Telegram ID в `.env`.

### Conflict: terminated by other getUpdates request

Запущено две копии одного и того же бота. Остановите лишний запуск: локальный PyCharm, Railway, Render или VPS.

---

## 11. Что можно улучшить дальше

- добавить Google Sheets;
- добавить оплату через LiqPay / WayForPay;
- добавить WebApp-админку;
- добавить красивые карточки примеров;
- добавить автодожим через отложенные сообщения;
- добавить экспорт заявок в Excel.
