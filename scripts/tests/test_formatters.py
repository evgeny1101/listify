from unittest.mock import AsyncMock

import pytest

from bot.formatters import format_note_full, format_note_short, send_notes_in_chunks


class TestFormatNoteFull:
    def test_format_note_full_returns_formatted_string(self):
        result = format_note_full(1, "Test note")

        assert "📌 #1" in result
        assert "Test note" in result
        assert "═══" in result
        assert "───" in result

    def test_format_note_full_different_index(self):
        result = format_note_full(5, "Some text")

        assert "📌 #5" in result
        assert "Some text" in result


class TestFormatNoteShort:
    def test_format_note_short_returns_truncated_text(self):
        long_text = "A" * 50
        result = format_note_short(1, long_text)

        assert "..." in result
        assert "📌 #1" in result

    def test_format_note_short_returns_full_text_when_short(self):
        short_text = "Short note"
        result = format_note_short(1, short_text)

        assert "Short note" in result
        assert "..." not in result

    def test_format_note_short_custom_limit(self):
        text = "A" * 30
        result = format_note_short(1, text, limit=10)

        assert "..." in result


class TestSendNotesInChunks:
    @pytest.mark.asyncio
    async def test_send_notes_in_chunks_sends_single_message(self, sample_notes):
        mock_message = AsyncMock()
        mock_message.answer = AsyncMock()

        notes = [
            type("Note", (), {"id": 1, "text": "Note 1"})(),
            type("Note", (), {"id": 2, "text": "Note 2"})(),
        ]

        await send_notes_in_chunks(mock_message, notes, format_note_full)

        assert mock_message.answer.call_count == 1

    @pytest.mark.asyncio
    async def test_send_notes_in_chunks_splits_large_message(self, sample_notes):
        mock_message = AsyncMock()
        mock_message.answer = AsyncMock()

        long_text = "A" * 2000
        notes = [type("Note", (), {"id": i, "text": long_text})() for i in range(1, 5)]

        await send_notes_in_chunks(mock_message, notes, format_note_full)

        assert mock_message.answer.call_count >= 2

    @pytest.mark.asyncio
    async def test_send_notes_in_chunks_empty_list(self):
        mock_message = AsyncMock()
        mock_message.answer = AsyncMock()

        await send_notes_in_chunks(mock_message, [], format_note_full)

        mock_message.answer.assert_not_called()
