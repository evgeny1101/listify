# Changelog

All notable changes to this project will be documented in this file.

## [1.4.3] - 2026-05-11

### Fixed
- Исправлено удаление через `/del`: callback теперь использует `note_id` из БД, что корректно работает при несмежных ID
- Исправлено падение `/ls` из-за лишнего аргумента `note_id` в вызове `send_note_with_image()`
- Исправлен `IntegrityError` при добавлении/редактировании заметки с одним размером фото: для `small` используется fallback на `large` file_id

### Changed
- Удален неиспользуемый параметр `from_command` в `_process_photo()`

---

## [1.4.2] - 2026-05-04

### Changed
- Текст ежедневного уведомления стал более дружелюбным
- Обновлена документация (убрано устаревшее число тестов из AGENTS.md)

---

## [1.4.1] - 2026-05-04

### Fixed
- При редактировании фото `edited_at` не записывался
- Превью заметки при редактировании без времени
- Пустой текст при редактировании мог очистить заметку
- `DEFAULT_TZ_OFFSET=abc` в `.env` ронял бот при старте

### Changed
- Версионирование миграций через `PRAGMA user_version` вместо try/except
- `add_note()` возвращает `0` вместо `None` (безопасный fallback)

### Removed
- Мёртвый код `if args_text` в `/add` без аргументов

---

## [1.4.0] - 2026-05-04

### Added
- Время создания/редактирования заметок (формат `hh:mm dd.mm`)
- Переменная `DEFAULT_TZ_OFFSET` для настройки часового пояса (по умолчанию +3)
- Отображение времени в списке заметок, удалении и редактировании

### Changed
- Время заметки теперь берётся из Telegram (`message.date`), а не генерируется сервером

---

## [1.3.0] - 2026-04-27

### Added
- Ежедневные уведомления в 17:00 (если есть заметки)
- Переменная `NOTIFICATION_TIME` в `.env` для настройки времени

---

## [1.2.0] - 2026-04-18

### Added
- Inline кнопка удаления в /ls (удаление заметки прямо из списка)

### Fixed
- Удаление изображений при удалении заметки
- Сохранение текста при добавлении фото после команды /add
- Очистка state после добавления фото

---

## [1.1.0] - 2026-04-15

### Added
- Команда `/edit` для редактирования заметок
- Поддержка замены изображения при редактировании

### Changed
- Улучшено переключение между `/del` и `/edit`
- Убран показ списка заметок при `/del` и `/edit` без аргументов

### Fixed
- Исправлен баг: кнопка "Отмена" при удалении не работала

---

## [1.0.3] - 2026-04-15

### Added
- Multi-platform сборка (amd64, arm64)

### Changed
- docker-compose.yml использует ghcr.io образ вместо локального build
- Тесты перенесены в корень проекта (`tests/`)

### Removed
- Удалён скрипт `pack_for_deploy.py`
- Удалена папка `scripts/`

---

## [1.0.2] - 2026-04-15

### Added
- GitHub Actions workflow для Docker build & push в ghcr.io

---

## [1.0.1] - 2026-04-15

### Refactored
- Reorder middlewares for early access denial
- Unify callback_data format in keyboards
- Replace type() with SimpleNamespace and move imports
- Move load_dotenv to main.py and fix import order
- Remove dead code _disable_foreign_keys
- Make orphan image policy explicit

### Fixed
- Remove dead test fixtures and fix broken bot startup test

### Changed
- Update test path and harden startup config

### Added
- Add pack_for_deploy.py script

---

## [1.0.0] - 2026-04-13

### Added
- README и LICENSE (MIT)
- Docker поддержка (Dockerfile + docker-compose)
- Контроль доступа (whitelist пользователей)
- Поддержка изображений в заметках (оригинал + превью)
- Логирование с user_id и командой
- FSM для ввода заметок
- Поддержка диапазонов в /del (1-3)
- Поддержка нескольких ID в /del (1,2,3)
- Подтверждение удаления
- Отмена ввода
- Context7 MCP для документации

### Changed
- Переименована команда /list → /ls
- Лимит заметки 200 символов
- Разделены requirements.txt и requirements-dev.txt

### Fixed
- Обработка None в message.text
- Игнорирование caption начинающегося с /
- Ошибки с большими диапазонами ID
- Дубликаты ID в подтверждении удаления
- Переполнение при большом диапазоне в /del

---

## Формат

| Тип | Описание |
|-----|----------|
| `Added` | Новые функции |
| `Changed` | Изменения в существующих |
| `Fixed` | Исправления багов |
