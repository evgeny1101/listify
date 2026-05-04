from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.formatters import send_note_with_image
from config import DEFAULT_TZ_OFFSET
from database import get_note_images, get_notes
from keyboards import get_delete_button

router = Router()


@router.message(Command("ls"))
async def cmd_list(message: Message):
    notes = await get_notes()

    if not notes:
        await message.answer("📭 Записей пока нет")
        return

    for i, note in enumerate(notes, 1):
        images = await get_note_images(note.id) if note.has_image else []
        keyboard = get_delete_button(i)

        kwargs = {
            "message": message,
            "index": i,
            "text": note.text,
            "images": images,
            "reply_markup": keyboard,
            "created_at": note.created_at,
            "edited_at": note.edited_at,
            "offset": DEFAULT_TZ_OFFSET,
        }

        if images:
            kwargs["use_large"] = True
        else:
            kwargs["images"] = []
            kwargs["use_large"] = False

        await send_note_with_image(**kwargs)
