from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

MAX_MESSAGE_LENGTH = 4000
NOTE_SEPARATOR = "═"
NOTE_DELIMITER = "─"


def format_note(index: int, text: str) -> str:
    header = f"📌 #{index} {NOTE_SEPARATOR * 3}"
    footer = NOTE_DELIMITER * len(header)
    return f"{header}\n{text}\n{footer}"


async def send_notes_in_chunks(message: Message, notes):
    chunks = []
    current_chunk = ""

    for i, note in enumerate(notes, 1):
        formatted = format_note(i, note.text)
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


@router.message(Command("list"))
async def cmd_list(message: Message):
    from database import get_notes

    notes = await get_notes()

    if not notes:
        await message.answer("📭 Записей пока нет")
        return

    await send_notes_in_chunks(message, notes)
