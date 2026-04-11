---
name: lint
description: Запускает линтинг проекта через ruff (check + format)
---

## Что делает
1. source venv/bin/activate
2. ruff check . --fix
3. ruff format .
4. ruff check .

## Проверки
- Ruff check --fix — исправляет автоматические ошибки
- Ruff format — форматирует код
- Ruff check — финальная проверка