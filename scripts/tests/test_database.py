from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from database.db import add_note, delete_note, get_notes, init_db


class TestInitDb:
    @pytest.mark.asyncio
    async def test_init_db_creates_table(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_connection = AsyncMock()
            mock_aiosqlite.connect.return_value = mock_connection

            await init_db()

            mock_aiosqlite.connect.assert_called_once()


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
                "created_at": "2024-01-01T10:00:00",
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
