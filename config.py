import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    message_history_limit: int = 12
    rate_limit_seconds: float = 2.0


    @staticmethod
    def from_env() -> "Settings":
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        message_history_limit = int(os.getenv("MESSAGE_HISTORY_LIMIT", "12"))
        rate_limit_seconds = float(os.getenv("RATE_LIMIT_SECONDS", "2"))

        if not telegram_token:
            raise RuntimeError("TELEGRAM_TOKEN is not set")
        if not openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        return Settings(
            telegram_token=telegram_token,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            message_history_limit=message_history_limit,
            rate_limit_seconds=rate_limit_seconds,
        )
