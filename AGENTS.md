# Listify - Telegram Bot для заметок

## Запуск

```bash
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Настройка токена: создать `.env` с `BOT_TOKEN=ваш_токен`

## Зависимости

- aiogram==3.4.1 — Telegram Bot API
- aiosqlite==0.20.0 — асинхронный SQLite
- python-dotenv==1.0.1 — работа с .env

## Структура

- `main.py` — точка входа
- `bot/` — Bot, Dispatcher, Storage
- `handlers/` — обработчики команд
- `database/` — SQLite (aiosqlite)
- `models/` — dataclass Note

## Разработка

- Линтинг: `pip install ruff && ruff check . && ruff format .`
- Тесты: отсутствуют
- Сброс БД: `rm listify.db`