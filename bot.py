import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from database import init_db
from handlers import user, admin
from olx_email_watcher import watch_olx_email
import os

async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(user.router)

    # --- OLX EMAIL WATCHER ---
    asyncio.create_task(
        watch_olx_email(
            bot=bot,
            admin_ids=config.admin_ids,
            email_login=os.getenv("OLX_EMAIL_LOGIN"),
            email_password=os.getenv("OLX_EMAIL_PASSWORD"),
        )
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
