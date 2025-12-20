import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import Settings
from deepseek_client import DeepSeekService


SYSTEM_PROMPT = (
    "Ты — полезный ассистент. Отвечай по-русски, вежливо и понятно. "
    "Не пиши слишком длинные ответы, если пользователь не просит об этом."
)


@dataclass
class UserSession:
    history: Deque[dict]
    last_request_at: float = 0.0


class DialogManager:
    def __init__(self, history_limit: int) -> None:
        self._history_limit = history_limit
        self._sessions: Dict[int, UserSession] = {}

    def get_history(self, user_id: int) -> Deque[dict]:
        session = self._sessions.setdefault(
            user_id, UserSession(history=deque(maxlen=self._history_limit))
        )
        return session.history

    def reset(self, user_id: int) -> None:
        self._sessions.pop(user_id, None)

    def update_last_request(self, user_id: int) -> None:
        session = self._sessions.setdefault(
            user_id, UserSession(history=deque(maxlen=self._history_limit))
        )
        session.last_request_at = time.monotonic()

    def can_request(self, user_id: int, min_interval: float) -> bool:
        session = self._sessions.get(user_id)
        if session is None:
            return True
        return (time.monotonic() - session.last_request_at) >= min_interval


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Привет! Я бот, который отвечает с помощью DeepSeek. "
        "Просто напишите сообщение, и я отвечу.\n\n"
        "Доступные команды:\n"
        "/help — инструкция\n"
        "/reset — очистить историю диалога"
    )
    await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Напишите сообщение — я отвечу с помощью ИИ.\n"
        "Контекст диалога хранится отдельно для каждого пользователя.\n"
        "Команды:\n"
        "/start — приветствие\n"
        "/help — инструкция\n"
        "/reset — очистить историю диалога"
    )
    await update.message.reply_text(message)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dialog_manager: DialogManager = context.application.bot_data["dialog_manager"]
    dialog_manager.reset(update.effective_user.id)
    await update.message.reply_text("История диалога очищена. Можно начать заново!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    user_id = update.effective_user.id
    dialog_manager: DialogManager = context.application.bot_data["dialog_manager"]
    settings: Settings = context.application.bot_data["settings"]
    deepseek_service: DeepSeekService = context.application.bot_data["deepseek_service"]

    if not dialog_manager.can_request(user_id, settings.rate_limit_seconds):
        await update.message.reply_text(
            "Вы отправляете сообщения слишком часто. Попробуйте немного позже."
        )
        return

    dialog_manager.update_last_request(user_id)

    user_text = update.message.text.strip()
    history = dialog_manager.get_history(user_id)
    history.append({"role": "user", "content": user_text})

    messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)

    try:
        response_text = await asyncio.to_thread(deepseek_service.generate, messages)
    except Exception:
        logging.exception("DeepSeek request failed")
        await update.message.reply_text("Сервис временно недоступен. Попробуйте позже.")
        return

    history.append({"role": "assistant", "content": response_text})
    await update.message.reply_text(response_text, parse_mode=ParseMode.HTML)


def build_application(settings: Settings) -> Application:
    dialog_manager = DialogManager(settings.message_history_limit)
    deepseek_service = DeepSeekService(
        api_key=settings.deepseek_api_key,
        model=settings.deepseek_model,
        base_url=settings.deepseek_base_url,
    )

    application = Application.builder().token(settings.telegram_token).build()
    application.bot_data["dialog_manager"] = dialog_manager
    application.bot_data["settings"] = settings
    application.bot_data["deepseek_service"] = deepseek_service

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    settings = Settings.from_env()
    application = build_application(settings)
    application.run_polling()


if __name__ == "__main__":
    main()
