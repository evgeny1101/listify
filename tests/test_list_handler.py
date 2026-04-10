import pytest
from unittest.mock import AsyncMock, patch

from handlers.list import cmd_list


class TestCmdList:
    @pytest.mark.asyncio
    async def test_cmd_list_empty_shows_message(self, mock_message):
        with patch("handlers.list.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            await cmd_list(mock_message)

            mock_message.answer.assert_called_with("📭 Записей пока нет")

    @pytest.mark.asyncio
    async def test_cmd_list_with_notes_sends_messages(self, mock_message, sample_notes):
        with patch("handlers.list.get_notes", new_callable=AsyncMock) as mock_get:
            with patch(
                "handlers.list.get_note_images", new_callable=AsyncMock
            ) as mock_images:
                with patch(
                    "handlers.list.send_note_with_image", new_callable=AsyncMock
                ) as mock_send:
                    mock_get.return_value = sample_notes
                    mock_images.return_value = []

                    await cmd_list(mock_message)

                    mock_send.assert_called()

    @pytest.mark.asyncio
    async def test_cmd_list_gets_notes_from_db(self, mock_message):
        with patch("handlers.list.get_notes", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            await cmd_list(mock_message)

            mock_get.assert_called_once()
