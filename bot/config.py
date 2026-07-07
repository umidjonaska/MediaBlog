import os
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    token: str = os.getenv("BOT_TOKEN", "")
    api_base_url: str = os.getenv("APP_URL", "http://127.0.0.1:8000")

    admin_chat_ids: list[int] = [
        int(chat_id.strip())
        for chat_id in os.getenv("ADMIN_CHAT_IDS", "").split(",")
        if chat_id.strip()
    ]


config = BotConfig()

if not config.token:
    raise RuntimeError("BOT_TOKEN .env faylida topilmadi")

if not config.admin_chat_ids:
    raise RuntimeError("ADMIN_CHAT_IDS .env faylida topilmadi yoki bo'sh")