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
- pytest==8.0.0 — тестирование
- pytest-asyncio==0.23.5 — async тесты

## Структура

- `main.py` — точка входа
- `bot/` — Bot, Dispatcher, Storage
- `handlers/` — обработчики команд
- `database/` — SQLite (aiosqlite)
- `models/` — dataclass Note

## Разработка

- Линтинг: использовать скил `/lint`
- Тесты: использовать скил `/test` (42 теста, покрытие database, handlers, formatters)
- При внесении изменений: сначала добавить/обновить тесты, затем запустить `/test`
- Запуск тестов вручную: `python -m pytest tests/ -v`
- Сброс БД: `rm listify.db`

## Скилы

- `/lint` — запуск линтинга проекта
- `/test` — запуск тестов проекта