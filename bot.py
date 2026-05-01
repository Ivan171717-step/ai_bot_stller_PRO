import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from database import init_db
from handlers import user, admin

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_router(admin.router)
    dp.include_router(user.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
