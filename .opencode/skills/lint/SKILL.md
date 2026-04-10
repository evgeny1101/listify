---
name: lint
description: Запускает линтинг проекта через ruff (check + format)
---

## Что делает
1. source venv/bin/activate
2. ruff check . --fix
3. ruff format .