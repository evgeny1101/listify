from aiogram.types import Message

NOTE_SEPARATOR = "═"
NOTE_DELIMITER = "─"
MAX_MESSAGE_LENGTH = 4000


def format_note_full(index: int, text: str) -> str:
    header = f"📌 #{index} {NOTE_SEPARATOR * 3}"
    footer = NOTE_DELIMITER * len(header)
    return f"{header}\n{text}\n{footer}"


def format_note_short(index: int, text: str, limit: int = 25) -> str:
    header = f"📌 #{index} {NOTE_SEPARATOR * 3}"
    footer = NOTE_DELIMITER * len(header)
    truncated = text[:limit] + "..." if len(text) > limit else text
    return f"{header}\n{truncated}\n{footer}"


async def send_notes_in_chunks(message: Message, notes, format_func):
    chunks = []
    current_chunk = ""

    for i, note in enumerate(notes, 1):
        formatted = format_func(i, note.text)
        if len(current_chunk) + len(formatted) + 1 > MAX_MESSAGE_LENGTH:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = formatted
        else:
            if current_chunk:
                current_chunk += "\n" + formatted
            else:
                current_chunk = formatted

    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        await message.answer(chunk)