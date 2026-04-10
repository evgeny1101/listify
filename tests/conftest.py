from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio


@pytest.fixture
def mock_db_cursor():
    cursor = AsyncMock()
    cursor.lastrowid = 1
    cursor.rowcount = 1
    return cursor


@pytest_asyncio.fixture
async def mock_db_connection(mock_db_cursor):
    connection = AsyncMock()
    connection.execute = AsyncMock(return_value=mock_db_cursor)
    connection.__aenter__ = AsyncMock(return_value=connection)
    connection.__aexit__ = AsyncMock(return_value=None)
    return connection


@pytest.fixture
def mock_aiosqlite(mock_db_connection):
    with patch("database.db.aiosqlite") as mock:
        mock.connect = AsyncMock(return_value=mock_db_connection)
        yield mock


@pytest.fixture
def mock_message():
    message = AsyncMock()
    message.message_id = 1
    message.text = ""
    message.photo = None
    message.video = None
    message.document = None
    message.voice = None
    message.audio = None
    message.sticker = None
    message.animation = None
    message.caption = None
    message.answer = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 123
    message.chat = MagicMock()
    message.chat.id = 456
    return message


@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.get_state = AsyncMock(return_value=None)
    return state


@pytest.fixture
def mock_callback_query():
    callback = AsyncMock()
    callback.data = "cancel_input"
    callback.answer = AsyncMock()
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()
    return callback


@pytest.fixture
def mock_callback():
    callback = AsyncMock()
    callback.data = "confirm_delete:1"
    callback.answer = AsyncMock()
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()
    return callback


@pytest.fixture
def sample_notes():
    return [
        type(
            "Note",
            (),
            {
                "id": 1,
                "text": "First note",
                "created_at": "2024-01-01T10:00:00",
                "has_image": False,
            },
        )(),
        type(
            "Note",
            (),
            {
                "id": 2,
                "text": "Second note",
                "created_at": "2024-01-02T10:00:00",
                "has_image": False,
            },
        )(),
        type(
            "Note",
            (),
            {
                "id": 3,
                "text": "Third note",
                "created_at": "2024-01-03T10:00:00",
                "has_image": False,
            },
        )(),
    ]


@pytest.fixture
def sample_notes_with_image():
    return [
        type(
            "Note",
            (),
            {
                "id": 1,
                "text": "Note with image",
                "created_at": "2024-01-01T10:00:00",
                "has_image": True,
            },
        )(),
        type(
            "Note",
            (),
            {
                "id": 2,
                "text": "Note without image",
                "created_at": "2024-01-02T10:00:00",
                "has_image": False,
            },
        )(),
    ]


@pytest.fixture
def sample_images():
    return [
        type(
            "NoteImage", (), {"note_id": 1, "size": "small", "file_id": "small_file_id"}
        )(),
        type(
            "NoteImage", (), {"note_id": 1, "size": "large", "file_id": "large_file_id"}
        )(),
    ]


@pytest.fixture
def mock_get_notes(sample_notes):
    with patch("handlers.list.get_notes", new_callable=AsyncMock) as mock:
        mock.return_value = sample_notes
        yield mock


@pytest.fixture
def mock_add_note():
    with patch("handlers.add.add_note", new_callable=AsyncMock) as mock:
        mock.return_value = 1
        yield mock


@pytest.fixture
def mock_add_note_image():
    with patch("handlers.add.add_note_image", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_photo():
    photo = MagicMock()
    photo.file_id = "test_file_id"
    return photo


@pytest.fixture
def mock_delete_note():
    with patch("handlers.delete.delete_note", new_callable=AsyncMock) as mock:
        mock.return_value = True
        yield mock
