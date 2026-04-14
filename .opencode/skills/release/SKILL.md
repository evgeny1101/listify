---
name: release
description: Процесс релиза: чеклист для создания тега и публикации в GitHub
---

## Чеклист перед созданием тега

### 1. Локальные изменения

- [ ] Все изменения закоммичены (проверить через git status)
- [ ] Линтинг: `/lint`
- [ ] Тесты: `/test`

### 2. Версии (обновить до создания тега)

- [ ] `CHANGELOG.md`: добавить новую секцию сверху (копировать формат предыдущих)
- [ ] `pyproject.toml`: version = "X.X.X"
- [ ] `docker-compose.yml`: image: ghcr.io/evgeny1101/listify:vX.X.X

### 3. Релиз

- [ ] Запушить все коммиты: `git push origin master`
- [ ] Создать и запушить тег: `git tag vX.X.X && git push origin vX.X.X`
- [ ] Проверить GitHub Actions: https://github.com/evgeny1101/listify/actions
- [ ] Проверить Docker образ: https://github.com/evgeny1101/listify/pkgs/container/listify

---

## Типы изменений в CHANGELOG

| Тип | Описание |
|-----|----------|
| Added | Новые функции |
| Changed | Изменения в существующих |
| Fixed | Исправления багов |
| Removed | Удалён функционал |

---

## Пример CHANGELOG секции

```markdown
## [1.0.0] - 2026-04-15

### Added
- Новая функция

---

## [0.9.0] - 2026-04-13
...
```