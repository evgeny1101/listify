from __future__ import annotations

from collections.abc import Callable

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

from models.note import Note, NoteImage

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


async def send_notes_in_chunks(
    message: Message,
    notes: list[Note],
    format_func: Callable[[int, str], str],
) -> None:
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


async def send_note_with_image(
    message: Message,
    index: int,
    text: str,
    images: list[NoteImage],
    use_large: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> bool:
    header = f"📌 #{index} {NOTE_SEPARATOR * 3}"
    footer = NOTE_DELIMITER * len(header)

    size = "large" if use_large else "small"
    image = next((img for img in images if img.size == size), None)

    if not image:
        image = next(iter(images), None)

    full_text = f"{header}\n{text}\n{footer}" if text else header

    if image:
        try:
            await message.answer_photo(
                photo=image.file_id,
                caption=full_text,
                reply_markup=reply_markup,
            )
            return True
        except TelegramBadRequest:
            await message.answer(f"{full_text}\n⚠️ Изображение недоступно")
            return False

    await message.answer(full_text, reply_markup=reply_markup)
    return True


async def send_note_short_with_image(
    message: Message,
    index: int,
    text: str,
    images: list[NoteImage],
) -> bool:
    header = f"📌 #{index} {NOTE_SEPARATOR * 3}"
    footer = NOTE_DELIMITER * len(header)
    truncated = text[:25] + "..." if len(text) > 25 else text
    preview_text = f"{header}\n{truncated}\n{footer}" if text else header

    image = next((img for img in images if img.size == "small"), None)

    if not image:
        image = next(iter(images), None)

    if image:
        try:
            await message.answer_photo(
                photo=image.file_id,
                caption=preview_text,
            )
            return True
        except TelegramBadRequest:
            await message.answer(f"{preview_text}\n⚠️ Изображение недоступно")
            return False

    await message.answer(preview_text)
    return True
