import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: list[int]
    developer_username: str
    openai_api_key: str | None
    openai_model: str
    use_ai: bool


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Create .env from .env.example")
    raw_admins = os.getenv("ADMIN_IDS", "").replace(" ", "")
    admin_ids = [int(x) for x in raw_admins.split(",") if x]
    if not admin_ids:
        raise RuntimeError("ADMIN_IDS is not set. Add your Telegram user ID to .env")
    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        developer_username=os.getenv("DEVELOPER_USERNAME", "your_username").lstrip("@"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        use_ai=os.getenv("USE_AI", "false").lower() == "true",
    )

config = load_config()
