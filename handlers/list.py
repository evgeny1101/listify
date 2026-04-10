from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.formatters import format_note_full, send_notes_in_chunks
from database import get_notes

router = Router()


@router.message(Command("list"))
async def cmd_list(message: Message):
    notes = await get_notes()

    if not notes:
        await message.answer("📭 Записей пока нет")
        return

    await send_notes_in_chunks(message, notes, format_note_full)
