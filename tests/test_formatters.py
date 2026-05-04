from unittest.mock import AsyncMock

import pytest

from bot.formatters import (
    _build_note_body,
    format_note_full,
    format_note_short,
    format_timestamp,
    send_notes_in_chunks,
)


class TestFormatTimestamp:
    def test_format_timestamp_returns_formatted_with_offset(self):
        result = format_timestamp("2024-01-01T10:00:00+00:00", 3)

        assert result == "13:00 01.01"

    def test_format_timestamp_none_returns_empty(self):
        result = format_timestamp(None, 3)

        assert result == ""

    def test_format_timestamp_negative_offset(self):
        result = format_timestamp("2024-01-01T10:00:00+00:00", -5)

        assert result == "05:00 01.01"

    def test_format_timestamp_zero_offset(self):
        result = format_timestamp("2024-01-01T10:00:00+00:00", 0)

        assert result == "10:00 01.01"


class TestBuildNoteBody:
    def test_with_timestamp(self):
        result = _build_note_body(
            1, "Test", created_at="2024-01-01T10:00:00+00:00", offset=3
        )

        assert "📌 #1" in result
        assert "Test" in result
        assert "───" in result
        assert "13:00 01.01" in result

    def test_with_edited_at(self):
        result = _build_note_body(
            1,
            "Test",
            created_at="2024-01-01T10:00:00+00:00",
            edited_at="2024-01-02T14:00:00+00:00",
            offset=3,
        )

        assert "17:00 02.01" in result
        assert "13:00 01.01" not in result

    def test_without_timestamp(self):
        result = _build_note_body(1, "Test")

        assert "📌 #1" in result
        assert "Test" in result
        assert "───" in result
        assert ":" not in result.split("\n")[-1]


class TestFormatNoteFull:
    def test_format_note_full_returns_formatted_string(self):
        result = format_note_full(1, "Test note")

        assert "📌 #1" in result
        assert "Test note" in result
        assert "═══" in result
        assert "───" in result

    def test_format_note_full_with_timestamp(self):
        result = format_note_full(
            1, "Test", created_at="2024-01-01T10:00:00+00:00", offset=3
        )

        assert "13:00 01.01" in result

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

    def test_format_note_short_with_timestamp(self):
        result = format_note_short(
            1, "Test", created_at="2024-01-01T10:00:00+00:00", offset=3
        )

        assert "13:00 01.01" in result


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
