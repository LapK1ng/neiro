# neiro

Telegram-бот с интеграцией DeepSeek для диалогов на русском языке.

## Возможности

- Общение с пользователями через Telegram.
- Контекст диалога на пользователя (последние сообщения).
- Команды `/start`, `/help`, `/reset`.
- Защита от спама с ограничением частоты запросов.
- Обработка ошибок DeepSeek API и попытки повтора.

## Быстрый старт

1. Установите зависимости:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Создайте файл `.env` и заполните ключи:

```bash
cp .env.example .env
```

3. Запустите бота:

```bash
python bot.py
```

## Переменные окружения

- `TELEGRAM_TOKEN` — токен Telegram-бота.
- `DEEPSEEK_API_KEY` — ключ DeepSeek API.
- `DEEPSEEK_MODEL` — модель DeepSeek (по умолчанию `deepseek-chat`).
- `DEEPSEEK_BASE_URL` — базовый URL API (по умолчанию `https://api.deepseek.com`).
- `MESSAGE_HISTORY_LIMIT` — сколько последних сообщений хранить в контексте.
- `RATE_LIMIT_SECONDS` — минимальный интервал между запросами пользователя.

## Как работает бот

- При каждом сообщении пользователя бот проверяет частоту запросов.
- История диалога хранится отдельно для каждого `user_id` в памяти.
- В запрос к модели передаётся системное сообщение с правилами стиля ответа и история диалога.
- Ответ от DeepSeek отправляется обратно пользователю.

## Переключение на Webhook

По умолчанию используется long polling (`application.run_polling()`). Для перехода на webhook:

1. Разверните приложение на сервере с HTTPS (например, через Nginx + сертификат).
2. Замените запуск на `application.run_webhook(...)` и укажите:
   - `listen="0.0.0.0"`
   - `port` — ваш порт
   - `url_path` — путь для webhook
   - `webhook_url` — публичный URL
3. Убедитесь, что Telegram может достучаться до вашего сервера.

## Структура проекта

- `bot.py` — основная логика Telegram-бота.
- `config.py` — загрузка настроек из окружения.
- `deepseek_client.py` — работа с DeepSeek API.
- `.env.example` — пример переменных окружения.
- `requirements.txt` — зависимости проекта.
