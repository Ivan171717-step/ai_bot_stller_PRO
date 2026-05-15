import os
import uuid
from pathlib import Path
from typing import Tuple

from aiogram import Bot
from aiogram.types import Message
from openai import AsyncOpenAI

from config import config

VOICE_TMP_DIR = Path("data/voice_tmp")
MAX_VOICE_DURATION = 300


async def transcribe_voice(bot: Bot, message: Message) -> Tuple[str | None, str | None]:
    if not config.use_ai or not config.openai_api_key:
        return None, "Голосовое распознавание пока не подключено. Можно написать текстом."

    media = message.voice or message.audio
    if not media:
        return None, "Не удалось получить голосовое сообщение."

    duration = getattr(media, "duration", 0) or 0
    if duration > MAX_VOICE_DURATION:
        return None, "Голосовое слишком длинное. Отправьте запись короче 5 минут."

    VOICE_TMP_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".ogg" if message.voice else ".mp3"
    file_path = VOICE_TMP_DIR / f"{message.from_user.id}_{uuid.uuid4().hex}{ext}"

    try:
        tg_file = await bot.get_file(media.file_id)
        await bot.download_file(tg_file.file_path, destination=file_path)
    except Exception:
        if file_path.exists():
            file_path.unlink()
        return None, "Ошибка скачивания голосового. Попробуйте ещё раз или напишите текстом."

    client = AsyncOpenAI(api_key=config.openai_api_key)
    try:
        with open(file_path, "rb") as audio_file:
            result = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        text = (result.text or "").strip()
        if not text:
            return None, "Не удалось распознать речь. Попробуйте ещё раз или напишите текстом."
        return text, None
    except Exception:
        return None, "Ошибка распознавания голосового. Попробуйте ещё раз или напишите текстом."
    finally:
        if file_path.exists():
            file_path.unlink()
