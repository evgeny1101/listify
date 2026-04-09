from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("list"))
async def cmd_list(message: Message):
    from database import get_notes
    
    notes = await get_notes()
    
    if not notes:
        await message.answer("📭 Записей пока нет")
        return
    
    text = "📝 <b>Ваши записи:</b>\n\n"
    for i, note in enumerate(notes, 1):
        text += f"{i}. {note.text}\n"
    
    await message.answer(text, parse_mode="HTML")