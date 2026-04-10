from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.formatters import send_note_with_image
from database import get_note_images, get_notes

router = Router()


@router.message(Command("list"))
async def cmd_list(message: Message):
    notes = await get_notes()

    if not notes:
        await message.answer("📭 Записей пока нет")
        return

    for i, note in enumerate(notes, 1):
        images = await get_note_images(note.id) if note.has_image else []

        if images:
            await send_note_with_image(message, i, note.text, images, use_large=True)
        else:
            await send_note_with_image(message, i, note.text, [], use_large=False)
