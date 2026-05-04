import asyncio
import email
import imaplib
import logging
from email.header import decode_header

from aiogram import Bot


logger = logging.getLogger(__name__)
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


def decode_mime_text(value: str | None) -> str:
    """Decode email headers like Subject/From into readable text."""
    if not value:
        return ""

    parts = decode_header(value)
    result = ""

    for part, encoding in parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part

    return result.strip()


def build_olx_notification(message: email.message.Message) -> str:
    subject = decode_mime_text(message.get("Subject"))
    sender = decode_mime_text(message.get("From"))

    return (
        "📩 Новое сообщение с OLX\n\n"
        f"👤 От: {sender or 'OLX'}\n"
        f"📌 Тема: {subject or 'Новое сообщение'}\n\n"
        "Зайди в OLX и проверь чат."
    )


def fetch_unseen_olx_messages(email_login: str, email_password: str) -> list[email.message.Message]:
    """Read unseen OLX emails from Gmail and mark them as seen after fetch."""
    messages: list[email.message.Message] = []

    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(email_login, email_password)
        mail.select("INBOX")

        # Gmail/IMAP search: unread emails where sender contains 'olx'.
        status, found_ids = mail.search(None, '(UNSEEN FROM "olx")')
        if status != "OK" or not found_ids or not found_ids[0]:
            return messages

        for message_id in found_ids[0].split():
            status, data = mail.fetch(message_id, "(RFC822)")
            if status != "OK" or not data or not data[0]:
                continue

            raw_message = data[0][1]
            messages.append(email.message_from_bytes(raw_message))

    return messages


async def watch_olx_email(
    bot: Bot,
    admin_ids: list[int],
    email_login: str | None,
    email_password: str | None,
    interval_seconds: int = 60,
) -> None:
    """Periodically check Gmail for new OLX emails and notify admins in Telegram."""
    if not email_login or not email_password:
        logger.info("OLX email watcher is disabled: OLX_EMAIL_LOGIN or OLX_EMAIL_PASSWORD is empty.")
        return

    logger.info("OLX email watcher started.")

    while True:
        try:
            messages = await asyncio.to_thread(
                fetch_unseen_olx_messages,
                email_login,
                email_password,
            )

            for message in messages:
                notification = build_olx_notification(message)
                for admin_id in admin_ids:
                    await bot.send_message(admin_id, notification)

        except imaplib.IMAP4.error as error:
            logger.error("Gmail IMAP error while checking OLX emails: %s", error)
        except Exception:
            logger.exception("Unexpected error while checking OLX emails")

        await asyncio.sleep(interval_seconds)
