from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers.add import (
    MAX_NOTE_LENGTH,
    AddNote,
    _process_photo,
    add_note_content,
    cmd_add,
    get_photo_file_ids,
    has_unsupported_content,
    on_cancel_input,
    truncate_text,
)
from keyboards.cancel import get_cancel_keyboard


class TestTruncateText:
    def test_truncate_text_returns_unchanged_when_short(self):
        text = "Short note"
        result, truncated = truncate_text(text)

        assert result == "Short note"
        assert truncated is False

    def test_truncate_text_truncates_long_text(self):
        long_text = "A" * 300
        result, truncated = truncate_text(long_text)

        assert len(result) == MAX_NOTE_LENGTH
        assert truncated is True

    def test_truncate_text_exact_length_unchanged(self):
        text = "A" * MAX_NOTE_LENGTH
        result, truncated = truncate_text(text)

        assert len(result) == MAX_NOTE_LENGTH
        assert truncated is False


class TestHasUnsupportedContent:
    def test_has_unsupported_content_video(self, mock_message):
        mock_message.video = MagicMock()
        mock_message.document = None
        mock_message.voice = None
        mock_message.audio = None
        mock_message.sticker = None
        mock_message.animation = None

        assert has_unsupported_content(mock_message) is True

    def test_has_unsupported_content_document(self, mock_message):
        mock_message.video = None
        mock_message.document = MagicMock()
        mock_message.voice = None
        mock_message.audio = None
        mock_message.sticker = None
        mock_message.animation = None

        assert has_unsupported_content(mock_message) is True

    def test_has_unsupported_content_voice(self, mock_message):
        mock_message.video = None
        mock_message.document = None
        mock_message.voice = MagicMock()
        mock_message.audio = None
        mock_message.sticker = None
        mock_message.animation = None

        assert has_unsupported_content(mock_message) is True

    def test_has_unsupported_content_sticker(self, mock_message):
        mock_message.video = None
        mock_message.document = None
        mock_message.voice = None
        mock_message.audio = None
        mock_message.sticker = MagicMock()
        mock_message.animation = None

        assert has_unsupported_content(mock_message) is True

    def test_has_unsupported_content_text_only(self, mock_message):
        mock_message.video = None
        mock_message.document = None
        mock_message.voice = None
        mock_message.audio = None
        mock_message.sticker = None
        mock_message.animation = None

        assert has_unsupported_content(mock_message) is False


class TestGetPhotoFileIds:
    def test_get_photo_file_ids_with_multiple_photos(self, mock_message):
        mock_photo_small = MagicMock()
        mock_photo_small.file_id = "small_id"
        mock_photo_large = MagicMock()
        mock_photo_large.file_id = "large_id"

        mock_message.photo = [mock_photo_large, mock_photo_small]

        result = get_photo_file_ids(mock_message)

        assert result == ("large_id", "small_id")

    def test_get_photo_file_ids_with_single_photo(self, mock_message):
        mock_photo = MagicMock()
        mock_photo.file_id = "single_id"

        mock_message.photo = [mock_photo]

        result = get_photo_file_ids(mock_message)

        assert result == (None, "single_id")

    def test_get_photo_file_ids_no_photos(self, mock_message):
        mock_message.photo = []

        result = get_photo_file_ids(mock_message)

        assert result is None


class TestCmdAdd:
    @pytest.mark.asyncio
    async def test_cmd_add_with_text_adds_note(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add Test note"
        mock_message.photo = None

        await cmd_add(mock_message, mock_state)

        mock_add_note.assert_called_once_with("Test note")
        mock_message.answer.assert_called()
        mock_state.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_add_without_text_asks_for_input(self, mock_message, mock_state):
        mock_message.text = "/add"
        mock_message.photo = None

        await cmd_add(mock_message, mock_state)

        mock_message.answer.assert_called()
        mock_state.set_state.assert_called_once_with(AddNote.waiting_for_content)

    @pytest.mark.asyncio
    async def test_cmd_add_truncates_long_text(
        self, mock_message, mock_state, mock_add_note
    ):
        long_text = "A" * 300
        mock_message.text = f"/add {long_text}"
        mock_message.photo = None

        await cmd_add(mock_message, mock_state)

        mock_add_note.assert_called_once()
        called_text = mock_add_note.call_args[0][0]
        assert len(called_text) == MAX_NOTE_LENGTH
        assert "обрезано" in mock_message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_cmd_add_trims_whitespace(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add    Spaced note   "
        mock_message.photo = None

        await cmd_add(mock_message, mock_state)

        mock_add_note.assert_called_once_with("Spaced note")

    @pytest.mark.asyncio
    async def test_cmd_add_with_video_shows_error(self, mock_message, mock_state):
        mock_message.text = "/add"
        mock_message.photo = None
        mock_message.video = MagicMock()

        await cmd_add(mock_message, mock_state)

        mock_message.answer.assert_called_once()
        assert (
            "Поддерживаются только текст и изображения"
            in mock_message.answer.call_args[0][0]
        )

    @pytest.mark.asyncio
    async def test_cmd_add_with_document_shows_error(self, mock_message, mock_state):
        mock_message.text = "/add"
        mock_message.photo = None
        mock_message.document = MagicMock()

        await cmd_add(mock_message, mock_state)

        mock_message.answer.assert_called_once()
        assert (
            "Поддерживаются только текст и изображения"
            in mock_message.answer.call_args[0][0]
        )


class TestAddNoteContent:
    @pytest.mark.asyncio
    async def test_add_note_content_adds_and_answers(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "New note"
        mock_message.photo = None

        await add_note_content(mock_message, mock_state)

        mock_add_note.assert_called_once_with("New note")
        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_add_note_content_truncates_long_text(
        self, mock_message, mock_state, mock_add_note
    ):
        long_text = "A" * 300
        mock_message.text = long_text
        mock_message.photo = None

        await add_note_content(mock_message, mock_state)

        called_text = mock_add_note.call_args[0][0]
        assert len(called_text) == MAX_NOTE_LENGTH
        assert "обрезано" in mock_message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_add_note_content_intercepts_command_and_clears_state(
        self, mock_message, mock_state, mock_add_note, sample_notes
    ):
        mock_message.text = "/list"
        mock_message.photo = None

        with patch("handlers.list.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch("handlers.list.send_note_with_image", new_callable=AsyncMock):
                await add_note_content(mock_message, mock_state)

                mock_add_note.assert_not_called()
                mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_note_content_with_add_and_text_adds_note(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add my new note"
        mock_message.photo = None

        await add_note_content(mock_message, mock_state)

        mock_add_note.assert_called_once_with("my new note")
        mock_state.clear.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "добавлена" in call_args

    @pytest.mark.asyncio
    async def test_add_note_content_with_add_without_text_asks_for_input(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add"
        mock_message.photo = None

        await add_note_content(mock_message, mock_state)

        mock_add_note.assert_not_called()
        mock_state.clear.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "прервана" in call_args

    @pytest.mark.asyncio
    async def test_add_note_content_with_video_shows_error(
        self, mock_message, mock_state
    ):
        mock_message.text = "Some note"
        mock_message.photo = None
        mock_message.video = MagicMock()

        await add_note_content(mock_message, mock_state)

        mock_message.answer.assert_called_once()
        assert (
            "Поддерживаются только текст и изображения"
            in mock_message.answer.call_args[0][0]
        )

    @pytest.mark.asyncio
    async def test_add_note_content_empty_text_shows_error(
        self, mock_message, mock_state
    ):
        mock_message.text = "   "
        mock_message.photo = None

        await add_note_content(mock_message, mock_state)

        mock_message.answer.assert_called_once()
        assert "Введите текст заметки" in mock_message.answer.call_args[0][0]


class TestOnCancelInput:
    @pytest.mark.asyncio
    async def test_on_cancel_input_clears_state(self, mock_callback_query, mock_state):
        mock_callback_query.data = "cancel_add"
        await on_cancel_input(mock_callback_query, mock_state)

        mock_state.clear.assert_called_once()
        mock_callback_query.answer.assert_called_once()
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args[0][0]
        assert "отменён" in call_args

    @pytest.mark.asyncio
    async def test_on_cancel_input_edits_message(self, mock_callback_query, mock_state):
        mock_callback_query.data = "cancel_add"
        await on_cancel_input(mock_callback_query, mock_state)

        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args[0]
        assert "отменён" in call_args[0]


class TestCancelKeyboard:
    def test_get_cancel_keyboard_returns_markup(self):
        keyboard = get_cancel_keyboard()

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        assert keyboard.inline_keyboard[0][0].text == "Отмена"
        assert keyboard.inline_keyboard[0][0].callback_data == "cancel_add"

    @pytest.mark.asyncio
    async def test_cmd_add_without_text_has_cancel_button(
        self, mock_message, mock_state
    ):
        mock_message.text = "/add"
        mock_message.photo = None

        await cmd_add(mock_message, mock_state)

        call_kwargs = mock_message.answer.call_args[1]
        assert "reply_markup" in call_kwargs
        keyboard = call_kwargs["reply_markup"]
        assert keyboard is not None
        assert keyboard.inline_keyboard[0][0].callback_data == "cancel_add"


class TestProcessPhoto:
    @pytest.mark.asyncio
    async def test_process_photo_saves_both_sizes(
        self, mock_message, mock_state, mock_add_note, mock_add_note_image
    ):
        mock_photo1 = MagicMock()
        mock_photo1.file_id = "small_file_id"
        mock_photo2 = MagicMock()
        mock_photo2.file_id = "large_file_id"
        mock_message.photo = [mock_photo2, mock_photo1]
        mock_message.caption = None

        await _process_photo(mock_message, mock_state)

        mock_add_note.assert_called_once()
        mock_add_note_image.assert_called()

    @pytest.mark.asyncio
    async def test_process_photo_with_caption_saves_text(
        self, mock_message, mock_state, mock_add_note, mock_add_note_image
    ):
        mock_photo1 = MagicMock()
        mock_photo1.file_id = "small_file_id"
        mock_photo2 = MagicMock()
        mock_photo2.file_id = "large_file_id"
        mock_message.photo = [mock_photo2, mock_photo1]
        mock_message.caption = "My caption"

        await _process_photo(mock_message, mock_state)

        mock_add_note.assert_called_once_with("My caption")
        mock_add_note_image.assert_called()

    @pytest.mark.asyncio
    async def test_process_photo_without_caption_uses_default_text(
        self, mock_message, mock_state, mock_add_note, mock_add_note_image
    ):
        mock_photo1 = MagicMock()
        mock_photo1.file_id = "small_file_id"
        mock_photo2 = MagicMock()
        mock_photo2.file_id = "large_file_id"
        mock_message.photo = [mock_photo2, mock_photo1]
        mock_message.caption = None

        await _process_photo(mock_message, mock_state)

        mock_add_note.assert_called_once_with("📷 Изображение")

    @pytest.mark.asyncio
    async def test_process_photo_warns_multiple_images(
        self, mock_message, mock_state, mock_add_note, mock_add_note_image
    ):
        mock_photo1 = MagicMock()
        mock_photo1.file_id = "small_file_id"
        mock_photo2 = MagicMock()
        mock_photo2.file_id = "large_file_id"
        mock_photo3 = MagicMock()
        mock_photo3.file_id = "extra_file_id"
        mock_message.photo = [mock_photo3, mock_photo2, mock_photo1]
        mock_message.caption = None

        await _process_photo(mock_message, mock_state, from_command=True)

        call_args = mock_message.answer.call_args[0][0]
        assert "только первое" in call_args
