---
name: release
description: Процесс релиза: чеклист для создания тега и публикации в GitHub
---

## Чеклист перед созданием тега

### 1. Документация (до коммитов)

- [ ] README.md: проверить актуальность списка команд

### 2. Локальные изменения

- [ ] Все изменения закоммичены (проверить через git status)
- [ ] Линтинг: `/lint` (включает ruff check + format)
- [ ] Тесты: `/test`

### 3. Версии (обновить до создания тега)

- [ ] `CHANGELOG.md`: добавить новую секцию сверху (копировать формат предыдущих)
- [ ] `pyproject.toml`: version = "X.X.X"
- [ ] `docker-compose.yml`: image: ghcr.io/evgeny1101/listify:vX.X.X

### 4. Релиз

- [ ] Запушить все коммиты: `git push origin master`
- [ ] Создать и запушить тег: `git tag vX.X.X && git push origin vX.X.X`

### 5. Пострелиз (проверить через gh)

```bash
# Проверить GitHub Actions
gh run list --repo evgeny1101/listify --limit 2

# Проверить Docker образ
gh api "users/evgeny1101/packages?package_type=container" -q '.[].name'
```

Ожидать: `completed success` для последнего workflow.

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