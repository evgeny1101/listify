from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from database.db import add_note, delete_note, get_note, get_notes, init_db, update_note


class _FakeCursor:
    def __init__(self, version: int = 1, columns: list[str] | None = None):
        self._version = version
        self._columns = columns

    async def fetchone(self):
        return (self._version,)

    async def fetchall(self):
        return [(i, col) for i, col in enumerate(self._columns or [])]


class TestInitDb:
    def _build_execute_mock(
        self, version: int = 1, table_info_cols: list[str] | None = None
    ):
        sql_log: list[str] = []

        async def fake_execute(sql, *args):
            sql_log.append(sql)
            if "PRAGMA user_version" in sql and "=" not in sql:
                return _FakeCursor(version=version)
            if "PRAGMA table_info" in sql:
                return _FakeCursor(columns=table_info_cols or [])
            return _FakeCursor(version=version)

        return fake_execute, sql_log

    def _build_connection(
        self, version: int = 1, table_info_cols: list[str] | None = None
    ):
        mock_connection = AsyncMock()
        execute_mock, sql_log = self._build_execute_mock(
            version=version, table_info_cols=table_info_cols
        )
        mock_connection.execute = execute_mock
        mock_connection.__aenter__.return_value = mock_connection
        mock_connection.__aexit__.return_value = None
        return mock_connection, sql_log

    @pytest.mark.asyncio
    async def test_init_db_creates_table(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection, _ = self._build_connection(version=1)
            mock_aiosqlite.connect.return_value = mock_connection

            await init_db()

            mock_aiosqlite.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_db_runs_migration_when_version_zero(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection, sql_log = self._build_connection(
                version=0, table_info_cols=["id", "text", "created_at"]
            )
            mock_aiosqlite.connect.return_value = mock_connection

            await init_db()

            assert "ALTER TABLE notes ADD COLUMN edited_at TEXT" in sql_log
            assert "PRAGMA user_version = 1" in sql_log

    @pytest.mark.asyncio
    async def test_init_db_skips_migration_when_column_exists(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection, sql_log = self._build_connection(
                version=0,
                table_info_cols=["id", "text", "created_at", "edited_at"],
            )
            mock_aiosqlite.connect.return_value = mock_connection

            await init_db()

            assert "ALTER TABLE" not in "".join(sql_log)
            assert "PRAGMA user_version = 1" in sql_log


class TestAddNote:
    @pytest.mark.asyncio
    async def test_add_note_inserts_and_returns_id(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.lastrowid = 5
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await add_note("Test note")

            assert result == 5

    @pytest.mark.asyncio
    async def test_add_note_with_custom_created_at(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.lastrowid = 1
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await add_note("Test", created_at="2026-05-04T12:00:00+00:00")

            assert result == 1
            mock_connection.execute.assert_any_call(
                "INSERT INTO notes (text, created_at) VALUES (?, ?)",
                ("Test", "2026-05-04T12:00:00+00:00"),
            )

    @pytest.mark.asyncio
    async def test_add_note_uses_provided_text(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.lastrowid = 1
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await add_note("Test")

            assert result == 1
            mock_connection.execute.assert_any_call(
                "INSERT INTO notes (text, created_at) VALUES (?, ?)", ("Test", ANY)
            )


class TestGetNotes:
    @pytest.mark.asyncio
    async def test_get_notes_returns_list_of_notes(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "id": 1,
                "text": "Test note",
                "created_at": "2024-01-01T10:00:00+00:00",
                "edited_at": None,
                "has_image": 0,
            }[key]
            mock_cursor = MagicMock()
            mock_cursor.fetchall = AsyncMock(return_value=[mock_row])

            mock_execute_result = MagicMock()
            mock_execute_result.__aenter__ = AsyncMock(return_value=mock_cursor)
            mock_execute_result.__aexit__ = AsyncMock(return_value=None)

            mock_connection = MagicMock()
            mock_connection.execute = MagicMock(return_value=mock_execute_result)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await get_notes()

            assert len(result) == 1
            assert result[0].id == 1
            assert result[0].text == "Test note"
            assert result[0].has_image is False

    @pytest.mark.asyncio
    async def test_get_notes_returns_empty_list_when_empty(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_cursor = MagicMock()
            mock_cursor.fetchall = AsyncMock(return_value=[])

            mock_execute_result = MagicMock()
            mock_execute_result.__aenter__ = AsyncMock(return_value=mock_cursor)
            mock_execute_result.__aexit__ = AsyncMock(return_value=None)

            mock_connection = MagicMock()
            mock_connection.execute = MagicMock(return_value=mock_execute_result)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await get_notes()

            assert result == []


class TestDeleteNote:
    @pytest.mark.asyncio
    async def test_delete_note_returns_true_when_deleted(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.rowcount = 1
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await delete_note(1)

            assert result is True

    @pytest.mark.asyncio
    async def test_delete_note_returns_false_when_not_found(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.rowcount = 0
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await delete_note(999)

            assert result is False


class TestUpdateNote:
    @pytest.mark.asyncio
    async def test_update_note_sets_edited_at(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.rowcount = 1
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await update_note(
                1, "Updated", edited_at="2026-05-04T12:00:00+00:00"
            )

            assert result is True
            mock_connection.execute.assert_any_call(
                "UPDATE notes SET text = ?, edited_at = ? WHERE id = ?",
                ("Updated", "2026-05-04T12:00:00+00:00", 1),
            )

    @pytest.mark.asyncio
    async def test_update_note_without_edited_at(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.rowcount = 1
            mock_connection.execute = AsyncMock(return_value=mock_cursor)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await update_note(1, "Updated")

            assert result is True
            mock_connection.execute.assert_any_call(
                "UPDATE notes SET text = ? WHERE id = ?", ("Updated", 1)
            )


class TestGetNote:
    @pytest.mark.asyncio
    async def test_get_note_returns_with_edited_at(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "id": 1,
                "text": "Note",
                "created_at": "2024-01-01T10:00:00+00:00",
                "edited_at": "2024-01-02T10:00:00+00:00",
                "has_image": 0,
            }[key]
            mock_cursor = MagicMock()
            mock_cursor.fetchone = AsyncMock(return_value=mock_row)

            mock_execute_result = MagicMock()
            mock_execute_result.__aenter__ = AsyncMock(return_value=mock_cursor)
            mock_execute_result.__aexit__ = AsyncMock(return_value=None)

            mock_connection = MagicMock()
            mock_connection.execute = MagicMock(return_value=mock_execute_result)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            result = await get_note(1)

            assert result is not None
            assert result.id == 1
            assert result.edited_at == "2024-01-02T10:00:00+00:00"
