import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    deepseek_api_key: str
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"
    message_history_limit: int = 12
    rate_limit_seconds: float = 2.0

    @staticmethod
    def from_env() -> "Settings":
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        message_history_limit = int(os.getenv("MESSAGE_HISTORY_LIMIT", "12"))
        rate_limit_seconds = float(os.getenv("RATE_LIMIT_SECONDS", "2"))

        if not telegram_token:
            raise RuntimeError("TELEGRAM_TOKEN is not set")
        if not deepseek_api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")

        return Settings(
            telegram_token=telegram_token,
            deepseek_api_key=deepseek_api_key,
            deepseek_model=deepseek_model,
            deepseek_base_url=deepseek_base_url,
            message_history_limit=message_history_limit,
            rate_limit_seconds=rate_limit_seconds,
        )
