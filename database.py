import json
from datetime import datetime
import aiosqlite

DB_PATH = "data/bot.db"

DEFAULT_SETTINGS = {
    "min_price": "2000",
    "max_price": "4000",
    "urgent_price": "1000",
    "deadline": "1–2 дня",
    "payment_terms": "Оплата по факту выполнения: после согласования, тестирования и передачи готового бота клиенту.",
}

DEFAULT_PACKAGES = [
    ("Старт", "Базовый бот: меню, кнопки, прием заявок, уведомления админу."),
    ("Бизнес", "Бот с CRM: заявки, база клиентов, статусы, таблица, админ-панель."),
    ("AI", "Умный бот: AI-консультант, ответы клиентам, заявки, база знаний."),
]

DEFAULT_EXAMPLES = [
    ("Бот для заявок", "Для услуг, ремонта, доставки, металлолома. Кнопки, форма заявки, уведомление админу, таблица клиентов."),
    ("Бот-магазин", "Каталог товаров, корзина, оформление заказа, оплата, админ-панель."),
    ("Бот с AI-консультантом", "Отвечает клиентам, консультирует, помогает выбрать услугу и принимает заявки 24/7."),
    ("Бот для записи", "Выбор услуги и времени, запись клиента, уведомления и история заявок."),
]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            phone TEXT,
            first_seen TEXT,
            applications_count INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            phone TEXT,
            business TEXT,
            bot_type TEXT,
            functions TEXT,
            payments TEXT,
            ai_needed TEXT,
            urgency TEXT,
            comment TEXT,
            estimated_price TEXT,
            status TEXT DEFAULT 'новая',
            created_at TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
        """)
        for key, value in DEFAULT_SETTINGS.items():
            await db.execute("INSERT OR IGNORE INTO settings(key, value) VALUES(?, ?)", (key, value))
        cur = await db.execute("SELECT COUNT(*) FROM packages")
        if (await cur.fetchone())[0] == 0:
            await db.executemany("INSERT INTO packages(name, description) VALUES(?, ?)", DEFAULT_PACKAGES)
        cur = await db.execute("SELECT COUNT(*) FROM examples")
        if (await cur.fetchone())[0] == 0:
            await db.executemany("INSERT INTO examples(title, description) VALUES(?, ?)", DEFAULT_EXAMPLES)
        await db.commit()

async def get_setting(key: str) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else ""

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key, value) VALUES(?, ?)", (key, value))
        await db.commit()

async def get_all_settings() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT key, value FROM settings")
        return {k: v for k, v in await cur.fetchall()}

async def get_packages():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, description FROM packages WHERE is_active=1 ORDER BY id")
        return await cur.fetchall()

async def add_package(name: str, description: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO packages(name, description) VALUES(?, ?)", (name, description))
        await db.commit()

async def get_examples():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, title, description FROM examples WHERE is_active=1 ORDER BY id")
        return await cur.fetchall()

async def add_example(title: str, description: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO examples(title, description) VALUES(?, ?)", (title, description))
        await db.commit()

async def save_application(user, data: dict, estimated_price: str) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = user.username or ""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        INSERT OR IGNORE INTO clients(user_id, username, name, phone, first_seen, applications_count)
        VALUES(?, ?, ?, ?, ?, 0)
        """, (user.id, username, data.get("name", ""), data.get("phone", ""), now))
        await db.execute("""
        UPDATE clients SET username=?, name=?, phone=?, applications_count=applications_count+1 WHERE user_id=?
        """, (username, data.get("name", ""), data.get("phone", ""), user.id))
        cur = await db.execute("""
        INSERT INTO applications(user_id, username, name, phone, business, bot_type, functions, payments, ai_needed, urgency, comment, estimated_price, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.id, username, data.get("name", ""), data.get("phone", ""), data.get("business", ""),
            data.get("bot_type", ""), data.get("functions", ""), data.get("payments", ""),
            data.get("ai_needed", ""), data.get("urgency", ""), data.get("comment", ""), estimated_price, now
        ))
        await db.commit()
        return cur.lastrowid

async def get_recent_applications(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name, phone, business, bot_type, status, created_at FROM applications ORDER BY id DESC LIMIT ?", (limit,))
        return await cur.fetchall()

async def get_application(app_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT * FROM applications WHERE id=?", (app_id,))
        return await cur.fetchone()

async def update_status(app_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        await db.commit()

async def stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM clients")
        clients = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM applications")
        apps = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM applications WHERE urgency LIKE '%сроч%' OR urgency LIKE '%Сроч%'")
        urgent = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM applications WHERE ai_needed LIKE '%Да%' OR ai_needed LIKE '%AI%'")
        ai = (await cur.fetchone())[0]
        return {"clients": clients, "apps": apps, "urgent": urgent, "ai": ai}
