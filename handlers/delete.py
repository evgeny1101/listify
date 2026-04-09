from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("del"))
async def cmd_del(message: Message):
    args = message.text.split()[1:]
    
    if not args:
        await message.answer("Укажите индекс записи.\nПример: /del 1")
        return
    
    try:
        index = int(args[0])
    except ValueError:
        await message.answer("Индекс должен быть числом")
        return
    
    from database import get_notes, delete_note
    
    notes = await get_notes()
    
    if not notes:
        await message.answer("Записей нет")
        return
    
    if index < 1 or index > len(notes):
        await message.answer(f"Неверный индекс. Введите от 1 до {len(notes)}")
        return
    
    note = notes[index - 1]
    await delete_note(note.id)
    await message.answer(f"✅ Запись #{index} удалена")