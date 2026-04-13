# Changelog

All notable changes to this project will be documented in this file.

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