# neiro

Telegram-бот с интеграцией ChatGPT для диалогов на русском языке.

## Возможности

- Общение с пользователями через Telegram.
- Контекст диалога на пользователя (последние сообщения).
- Команды `/start`, `/help`, `/reset`.
- Защита от спама с ограничением частоты запросов.
- Обработка ошибок OpenAI API и попытки повтора.
- Модерация запросов через официальный OpenAI moderation API.

## Быстрый старт

1. Установите зависимости:

```bash
python -m venv .venv
```

Активируйте виртуальное окружение в зависимости от вашей ОС/оболочки:

```bash
# Linux/macOS (bash/zsh)
source .venv/bin/activate
```

```bash
# Linux/macOS (fish)
source .venv/bin/activate.fish
```

```bash
# Windows (PowerShell)
.venv\\Scripts\\Activate.ps1
```

```bash
# Windows (cmd)
.venv\\Scripts\\activate.bat
```

После активации установите зависимости:

```bash
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
- `OPENAI_API_KEY` — ключ OpenAI API.
- `OPENAI_MODEL` — модель OpenAI (по умолчанию `gpt-4o-mini`).
- `MESSAGE_HISTORY_LIMIT` — сколько последних сообщений хранить в контексте.
- `RATE_LIMIT_SECONDS` — минимальный интервал между запросами пользователя.

## Как работает бот

- При каждом сообщении пользователя бот проверяет частоту запросов.
- Запрос проходит через moderation API. При флаге бот отказывается и предлагает безопасную альтернативу.
- История диалога хранится отдельно для каждого `user_id` в памяти.
- В запрос к модели передаётся системное сообщение с правилами стиля ответа и история диалога.
- Ответ от ChatGPT отправляется обратно пользователю.

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
- `openai_client.py` — работа с OpenAI API.
- `.env.example` — пример переменных окружения.
- `requirements.txt` — зависимости проекта.
