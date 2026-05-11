from unittest.mock import AsyncMock, patch

import pytest

from handlers.delete import (
    cmd_del,
    on_delete_confirm,
    on_ids_input,
    parse_ids,
    show_delete_confirm,
)


class TestParseIds:
    def test_parse_ids_returns_valid_ids(self):
        result = parse_ids("1, 2, 3")

        assert result == [1, 2, 3]

    def test_parse_ids_with_spaces(self):
        result = parse_ids(" 1 , 2 , 3 ")

        assert result == [1, 2, 3]

    def test_parse_ids_ignores_invalid(self):
        result = parse_ids("1, abc, 3")

        assert result == [1, 3]

    def test_parse_ids_empty_string(self):
        result = parse_ids("")

        assert result == []

    def test_parse_ids_single_id(self):
        result = parse_ids("5")

        assert result == [5]

    def test_parse_ids_range(self):
        result = parse_ids("1-3")

        assert result == [1, 2, 3]

    def test_parse_ids_range_with_spaces(self):
        result = parse_ids("1 - 3")

        assert result == [1, 2, 3]

    def test_parse_ids_range_reversed(self):
        result = parse_ids("3-1")

        assert result == [1, 2, 3]

    def test_parse_ids_mixed(self):
        result = parse_ids("1, 3-5, 7")

        assert result == [1, 3, 4, 5, 7]


class TestCmdDel:
    @pytest.mark.asyncio
    async def test_cmd_del_no_notes(self, mock_message, mock_state):
        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            await cmd_del(mock_message, mock_state)

            mock_message.answer.assert_called_with("Записей нет")

    @pytest.mark.asyncio
    async def test_cmd_del_without_args_shows_list(
        self, mock_message, mock_state, sample_notes
    ):
        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes

            await cmd_del(mock_message, mock_state)

            assert mock_state.set_state.called
            assert mock_message.answer.call_count == 1
            call_args = mock_message.answer.call_args[0][0]
            assert "ID" in call_args

    @pytest.mark.asyncio
    async def test_cmd_del_with_args_calls_confirm(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "/del 1, 2"

        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch(
                "handlers.delete.show_delete_confirm", new_callable=AsyncMock
            ) as mock_confirm:
                await cmd_del(mock_message, mock_state)
                mock_confirm.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_del_invalid_ids_shows_error(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "/del abc"

        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes

            await cmd_del(mock_message, mock_state)

            mock_message.answer.assert_called()


class TestOnIdsInput:
    @pytest.mark.asyncio
    async def test_on_ids_input_valid_ids_calls_confirm(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "1, 2"

        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            with patch(
                "handlers.delete.show_delete_confirm", new_callable=AsyncMock
            ) as mock_confirm:
                await on_ids_input(mock_message, mock_state)
                mock_confirm.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_ids_input_invalid_ids_shows_error(self, mock_message, mock_state):
        mock_message.text = "abc"

        with patch(
            "handlers.delete.show_delete_confirm", new_callable=AsyncMock
        ) as mock_confirm:
            await on_ids_input(mock_message, mock_state)
            mock_confirm.assert_not_called()
            mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_on_ids_input_empty_shows_error(self, mock_message, mock_state):
        mock_message.text = ""

        with patch(
            "handlers.delete.show_delete_confirm", new_callable=AsyncMock
        ) as mock_confirm:
            await on_ids_input(mock_message, mock_state)
            mock_confirm.assert_not_called()
            mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_on_ids_input_intercepts_command_clears_state(
        self, mock_message, mock_state
    ):
        mock_message.text = "/ls"

        await on_ids_input(mock_message, mock_state)

        mock_state.clear.assert_called_once()
        mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_ids_input_with_del_and_ids_calls_confirm(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "/del 1, 2"

        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            await on_ids_input(mock_message, mock_state)

            mock_state.clear.assert_called_once()
            mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_ids_input_with_del_without_ids_shows_list(
        self, mock_message, mock_state, sample_notes
    ):
        mock_message.text = "/del"

        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes
            await on_ids_input(mock_message, mock_state)

            mock_state.clear.assert_called_once()
            mock_message.answer.assert_not_called()


class TestShowDeleteConfirm:
    @pytest.mark.asyncio
    async def test_show_delete_confirm_valid_ids(
        self, mock_message, mock_state, sample_notes
    ):
        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes

            await show_delete_confirm(mock_message, [1, 2], mock_state)

            mock_state.update_data.assert_called()
            mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_show_delete_confirm_invalid_ids_shows_error(
        self, mock_message, mock_state, sample_notes
    ):
        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes

            await show_delete_confirm(mock_message, [999], mock_state)

            mock_message.answer.assert_called_with(
                "Неверные ID. Введите существующие номера записей."
            )

    @pytest.mark.asyncio
    async def test_show_delete_confirm_empty_ids_shows_error(
        self, mock_message, mock_state, sample_notes
    ):
        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes

            await show_delete_confirm(mock_message, [], mock_state)

            mock_message.answer.assert_called_with(
                "Неверные ID. Введите существующие номера записей."
            )

    @pytest.mark.asyncio
    async def test_show_delete_confirm_uses_note_ids_in_callback(
        self, mock_message, mock_state, sample_notes
    ):
        sample_notes[1].id = 10

        with patch("handlers.delete.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes

            await show_delete_confirm(mock_message, [2], mock_state)

            reply_markup = mock_message.answer.call_args_list[-1].kwargs["reply_markup"]
            confirm_button = reply_markup.inline_keyboard[0][0]
            cancel_button = reply_markup.inline_keyboard[0][1]

            assert confirm_button.callback_data == "confirm:delete:10"
            assert cancel_button.callback_data == "cancel:delete:10"


class TestDeleteNoteWithImages:
    @pytest.mark.asyncio
    async def test_delete_note_deletes_images_when_has_image(
        self,
        mock_callback_query,
        mock_state,
        sample_notes,
        mock_delete_note,
        mock_delete_note_images,
    ):
        sample_notes[0].has_image = True
        mock_callback_query.data = "confirm:delete:1"

        with patch("handlers.delete.get_note", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes[0]

            await on_delete_confirm(mock_callback_query, mock_state)

            mock_delete_note_images.assert_called_once_with(sample_notes[0].id)
            mock_delete_note.assert_called_once_with(sample_notes[0].id)

    @pytest.mark.asyncio
    async def test_delete_note_skips_image_delete_when_no_image(
        self,
        mock_callback_query,
        mock_state,
        sample_notes,
        mock_delete_note,
        mock_delete_note_images,
    ):
        sample_notes[0].has_image = False
        mock_callback_query.data = "confirm:delete:1"

        with patch("handlers.delete.get_note", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes[0]

            await on_delete_confirm(mock_callback_query, mock_state)

            mock_delete_note_images.assert_not_called()
            mock_delete_note.assert_called_once_with(sample_notes[0].id)

    @pytest.mark.asyncio
    async def test_cancel_single_restores_delete_button(
        self,
        mock_callback_query,
        mock_state,
        sample_notes,
    ):
        mock_callback_query.data = "cancel:delete:1"
        mock_callback_query.message.edit_reply_markup = AsyncMock()

        with patch("handlers.delete.get_note", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_notes[0]

            await on_delete_confirm(mock_callback_query, mock_state)

            assert mock_callback_query.message.edit_reply_markup.called
            reply_markup = (
                mock_callback_query.message.edit_reply_markup.call_args.kwargs[
                    "reply_markup"
                ]
            )
            button = reply_markup.inline_keyboard[0][0]
            assert button.callback_data == "delete:1"

    @pytest.mark.asyncio
    async def test_cancel_single_for_deleted_note_shows_message(
        self,
        mock_callback_query,
        mock_state,
    ):
        mock_callback_query.data = "cancel:delete:1"

        with patch("handlers.delete.get_note", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            await on_delete_confirm(mock_callback_query, mock_state)

            mock_callback_query.message.edit_text.assert_called_with(
                "Запись уже удалена", reply_markup=None
            )

    @pytest.mark.asyncio
    async def test_cancel_multiple_removes_keyboard(
        self,
        mock_callback_query,
        mock_state,
    ):
        mock_callback_query.data = "cancel:delete:1,2"
        mock_callback_query.message.edit_reply_markup = AsyncMock()

        await on_delete_confirm(mock_callback_query, mock_state)

        mock_callback_query.message.edit_reply_markup.assert_called_with(
            reply_markup=None
        )
