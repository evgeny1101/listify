import pytest
from unittest.mock import patch, AsyncMock

from handlers.add import truncate_text, cmd_add, add_note_text, AddNote, MAX_NOTE_LENGTH
from handlers.add import on_cancel_input
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


class TestCmdAdd:
    @pytest.mark.asyncio
    async def test_cmd_add_with_text_adds_note(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add Test note"

        await cmd_add(mock_message, mock_state)

        mock_add_note.assert_called_once_with("Test note")
        mock_message.answer.assert_called()
        mock_state.set_state.assert_not_called()

    @pytest.mark.asyncio
    async def test_cmd_add_without_text_asks_for_input(self, mock_message, mock_state):
        mock_message.text = "/add"

        await cmd_add(mock_message, mock_state)

        mock_message.answer.assert_called()
        mock_state.set_state.assert_called_once_with(AddNote.waiting_for_text)

    @pytest.mark.asyncio
    async def test_cmd_add_truncates_long_text(
        self, mock_message, mock_state, mock_add_note
    ):
        long_text = "A" * 300
        mock_message.text = f"/add {long_text}"

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

        await cmd_add(mock_message, mock_state)

        mock_add_note.assert_called_once_with("Spaced note")


class TestAddNoteText:
    @pytest.mark.asyncio
    async def test_add_note_text_adds_and_answers(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "New note"

        await add_note_text(mock_message, mock_state)

        mock_add_note.assert_called_once_with("New note")
        mock_state.clear.assert_called_once()
        mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_add_note_text_truncates_long_text(
        self, mock_message, mock_state, mock_add_note
    ):
        long_text = "A" * 300
        mock_message.text = long_text

        await add_note_text(mock_message, mock_state)

        called_text = mock_add_note.call_args[0][0]
        assert len(called_text) == MAX_NOTE_LENGTH
        assert "обрезано" in mock_message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_add_note_text_intercepts_command_and_clears_state(
        self, mock_message, mock_state, mock_add_note, sample_notes
    ):
        mock_message.text = "/list"

        with patch("handlers.list.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch("handlers.list.send_notes_in_chunks", new_callable=AsyncMock) as mock_send:
                await add_note_text(mock_message, mock_state)

                mock_add_note.assert_not_called()
                mock_state.clear.assert_called_once()
                mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_note_text_with_add_and_text_adds_note(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add my new note"

        await add_note_text(mock_message, mock_state)

        mock_add_note.assert_called_once_with("my new note")
        mock_state.clear.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "добавлена" in call_args

    @pytest.mark.asyncio
    async def test_add_note_text_with_add_without_text_asks_for_input(
        self, mock_message, mock_state, mock_add_note
    ):
        mock_message.text = "/add"

        await add_note_text(mock_message, mock_state)

        mock_add_note.assert_not_called()
        mock_state.clear.assert_called_once()
        call_args = mock_message.answer.call_args[0][0]
        assert "прервана" in call_args


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

        await cmd_add(mock_message, mock_state)

        call_kwargs = mock_message.answer.call_args[1]
        assert "reply_markup" in call_kwargs
        keyboard = call_kwargs["reply_markup"]
        assert keyboard is not None
        assert keyboard.inline_keyboard[0][0].callback_data == "cancel_add"
