from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers.add import MAX_NOTE_LENGTH
from handlers.edit import (
    EditNote,
    cmd_edit,
    edit_note_content,
    edit_note_id,
    on_cancel_edit,
    send_current_note,
)


class TestCmdEdit:
    @pytest.mark.asyncio
    async def test_cmd_edit_no_notes(self, mock_message, mock_state):
        mock_message.text = "/edit"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            await cmd_edit(mock_message, mock_state)

            mock_message.answer.assert_called_once_with("Записей нет")

    @pytest.mark.asyncio
    async def test_cmd_edit_without_args_shows_list(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "/edit"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch(
                "bot.formatters.send_note_short_with_image", new_callable=AsyncMock
            ):
                await cmd_edit(mock_message, mock_state)

                mock_state.set_state.assert_called_once_with(EditNote.waiting_for_id)
                mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_cmd_edit_with_valid_id_calls_content(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "/edit 1"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch(
                "handlers.edit.send_current_note", new_callable=AsyncMock
            ) as mock_send:
                await cmd_edit(mock_message, mock_state)

                mock_send.assert_called_once_with(mock_message, 1)
                mock_state.set_state.assert_called_once_with(
                    EditNote.waiting_for_content
                )

    @pytest.mark.asyncio
    async def test_cmd_edit_invalid_id_shows_error(self, mock_message, mock_state):
        mock_message.text = "/edit 999"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [{"id": 1, "text": "Note"}]
            await cmd_edit(mock_message, mock_state)

            mock_message.answer.assert_called_once_with("Запись не найдена")

    @pytest.mark.asyncio
    async def test_cmd_edit_with_video_shows_error(self, mock_message, mock_state):
        mock_message.text = "/edit"
        mock_message.photo = None
        mock_message.video = MagicMock()

        await cmd_edit(mock_message, mock_state)

        mock_message.answer.assert_called_once()
        assert (
            "Поддерживаются только текст и изображения"
            in (mock_message.answer.call_args[0][0])
        )

    @pytest.mark.asyncio
    async def test_cmd_edit_non_numeric_id_shows_error(self, mock_message, mock_state):
        mock_message.text = "/edit abc"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [{"id": 1, "text": "Note"}]
            await cmd_edit(mock_message, mock_state)

            mock_message.answer.assert_called_once_with("ID должен быть числом")


class TestEditNoteId:
    @pytest.mark.asyncio
    async def test_edit_note_id_valid_id_calls_content(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "1"
        mock_message.photo = None

        mock_state.get_data = AsyncMock(return_value={"note_index": 1, "note_db_id": 1})

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch(
                "handlers.edit.send_current_note", new_callable=AsyncMock
            ) as mock_send:
                await edit_note_id(mock_message, mock_state)

                mock_send.assert_called_once_with(mock_message, 1)
                mock_state.set_state.assert_called_once_with(
                    EditNote.waiting_for_content
                )

    @pytest.mark.asyncio
    async def test_edit_note_id_invalid_id_shows_error(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "999"
        mock_message.photo = None

        mock_state.get_data = AsyncMock(return_value={"note_index": 1, "note_db_id": 1})

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            await edit_note_id(mock_message, mock_state)

            mock_message.answer.assert_called_once_with("Запись не найдена")

    @pytest.mark.asyncio
    async def test_edit_note_id_empty_shows_error(self, mock_message, mock_state):
        mock_message.text = ""
        mock_message.photo = None

        await edit_note_id(mock_message, mock_state)

        mock_message.answer.assert_called_once_with("Введите ID записи")

    @pytest.mark.asyncio
    async def test_edit_note_id_non_numeric_shows_error(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "abc"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            await edit_note_id(mock_message, mock_state)

            mock_message.answer.assert_called_once_with("ID должен быть числом")

    @pytest.mark.asyncio
    async def test_edit_note_id_intercepts_command_clears_state(
        self, mock_message, mock_state
    ):
        mock_message.text = "/ls"
        mock_message.photo = None

        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            await edit_note_id(mock_message, mock_state)

            mock_state.clear.assert_called_once()
            mock_message.answer.assert_not_called()


class TestEditNoteContent:
    @pytest.mark.asyncio
    async def test_edit_note_content_updates_text(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "Updated text"
        mock_message.photo = None

        mock_state.get_data = AsyncMock(return_value={"note_index": 1, "note_db_id": 1})

        with patch("handlers.edit.get_notes", new_callable=AsyncMock):
            with patch(
                "handlers.edit.update_note", new_callable=AsyncMock
            ) as mock_update:
                await edit_note_content(mock_message, mock_state)

                mock_update.assert_called_once_with(1, "Updated text")
                mock_state.clear.assert_called_once()
                mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_edit_note_content_truncates_long_text(
        self, mock_message, mock_state, sample_notes
    ):
        long_text = "A" * 300
        mock_message.text = long_text
        mock_message.photo = None

        mock_state.get_data = AsyncMock(return_value={"note_index": 1, "note_db_id": 1})

        with patch("handlers.edit.get_notes", new_callable=AsyncMock):
            with patch(
                "handlers.edit.update_note", new_callable=AsyncMock
            ) as mock_update:
                await edit_note_content(mock_message, mock_state)

                called_text = mock_update.call_args[0][1]
                assert len(called_text) == MAX_NOTE_LENGTH
                assert "обрезано" in mock_message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_edit_note_content_empty_text_shows_error(
        self, mock_message, mock_state
    ):
        mock_message.text = ""
        mock_message.photo = None

        await edit_note_content(mock_message, mock_state)

        mock_message.answer.assert_called_once_with("⚠️ Введите текст заметки")

    @pytest.mark.asyncio
    async def test_edit_note_content_with_photo_updates_both(
        self, mock_message, mock_state, sample_notes
    ):
        mock_photo1 = MagicMock()
        mock_photo1.file_id = "small_file_id"
        mock_photo2 = MagicMock()
        mock_photo2.file_id = "large_file_id"
        mock_message.photo = [mock_photo2, mock_photo1]
        mock_message.caption = "New caption"
        mock_message.text = ""

        mock_state.get_data = AsyncMock(return_value={"note_index": 1, "note_db_id": 1})

        with patch("handlers.edit.get_notes", new_callable=AsyncMock):
            with patch("handlers.edit.update_note", new_callable=AsyncMock):
                with patch(
                    "handlers.edit.add_note_image", new_callable=AsyncMock
                ) as mock_add_image:
                    await edit_note_content(mock_message, mock_state)

                    assert mock_add_image.call_count == 2

    @pytest.mark.asyncio
    async def test_edit_note_content_intercepts_command_clears_state(
        self, mock_message, mock_state
    ):
        mock_message.text = "/ls"
        mock_message.photo = None

        await edit_note_content(mock_message, mock_state)

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_not_called()


class TestOnCancelEdit:
    @pytest.mark.asyncio
    async def test_on_cancel_edit_clears_state(self, mock_callback_query, mock_state):
        mock_callback_query.data = "cancel:edit"
        await on_cancel_edit(mock_callback_query, mock_state)

        mock_state.clear.assert_called_once()
        mock_callback_query.answer.assert_called_once()
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args[0][0]
        assert "отменено" in call_args

    @pytest.mark.asyncio
    async def test_on_cancel_edit_edits_message(self, mock_callback_query, mock_state):
        mock_callback_query.data = "cancel:edit"
        await on_cancel_edit(mock_callback_query, mock_state)

        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args[0]
        assert "отменено" in call_args[0]


class TestSendCurrentNote:
    @pytest.mark.asyncio
    async def test_send_current_note_valid_index(self, mock_message, sample_notes):
        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch(
                "handlers.edit.get_note_images", new_callable=AsyncMock
            ) as mock_images:
                mock_images.return_value = []
                with patch(
                    "bot.formatters.send_note_short_with_image", new_callable=AsyncMock
                ) as mock_send:
                    await send_current_note(mock_message, 1)

                    mock_send.assert_called_once()
                    mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_send_current_note_invalid_index(self, mock_message, sample_notes):
        with patch("handlers.edit.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            await send_current_note(mock_message, 999)

            mock_message.answer.assert_called_once_with("Запись не найдена")
