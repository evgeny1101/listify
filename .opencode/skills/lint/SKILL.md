---
name: lint
description: Запускает линтинг проекта через ruff (check + format + typecheck)
---

## Что делает
1. source venv/bin/activate
2. ruff check . --fix
3. ruff format .
4. ruff check . --select=RUF --type-checking-only