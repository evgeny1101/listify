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

Для разработки и тестов:
```bash
pip install -r requirements-dev.txt
```

## Структура

- `main.py` — точка входа
- `bot/` — Bot, Dispatcher, Storage
- `handlers/` — обработчики команд
- `database/` — SQLite (aiosqlite)
- `models/` — dataclass Note

## Разработка

- Линтинг: использовать скил `/lint` (включает typecheck)
- При добавлении новых функций: всегда добавлять аннотации типов
- Тесты: использовать скил `/test` (82 теста, покрытие database, handlers, formatters, middlewares)
- При внесении изменений: сначала добавить/обновить тесты, затем запустить `/test`
- Запуск тестов вручную: `python -m pytest tests/ -v`
- Сброс БД: `rm listify.db`
- Все изменения должны проходить lint + тесты перед завершением

## Скилы

- `/lint` — запуск линтинга проекта
- `/test` — запуск тестов проекта

## Context7 (MCP)

Для работы с документацией библиотек используется MCP context7:
- Запрос документации: `context7_resolve-library-id` + `context7_query-docs`
- Библиотека определяется автоматически по версии из requirements.txt (продакшен) или requirements-dev.txt (разработка)
- Примеры запросов: "aiogram filters", "aiosqlite async connection"