import pytest
from unittest.mock import AsyncMock, patch

from handlers.delete import parse_ids, cmd_del, on_ids_input, show_delete_confirm


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
            assert mock_message.answer.call_count >= 2

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
