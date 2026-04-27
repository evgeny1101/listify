# Listify

Telegram бот для заметок с изображениями.

> Написан с помощью [opencode](https://opencode.ai)

## Возможности

- Текстовые заметки до 200 символов
- Изображения (сохраняется оригинал + превью)
- Удаление одной или нескольких заметок
- Контроль доступа (whitelist пользователей)
- Ежедневные уведомления о заметках
- Docker

## Быстрый старт

```bash
# Клонировать
git clone https://github.com/Evgeniy1101/listify.git
cd listify

# Создать venv и установить зависимости
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Создать .env
cp .env.example .env
# Отредактировать .env: добавить BOT_TOKEN и ALLOWED_USERS
```

### ⚠️ Важно: Безопасность

По умолчанию бот **блокирует всех пользователей**. Добавьте свой Telegram ID в `ALLOWED_USERS`:

```
ALLOWED_USERS=YOUR_TELEGRAM_ID
```

Без этого бот не будет отвечать ни на какие сообщения.

## Команды

| Команда | Описание |
|---------|-----------|
| `/add` | добавить заметку (текст или изображение) |
| `/ls` | показать все заметки |
| `/edit N` | редактировать заметку N (текст и/или изображение) |
| `/del N` | удалить заметку N (или `1,2,3` / `1-3`) |
| `/help` | справка |

## Docker

```bash
docker-compose up -d
```

## Разработка

```bash
# Тесты
pytest

# Линтинг
ruff check . && ruff format .
```

## License

MIT