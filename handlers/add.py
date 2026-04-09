from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()


class AddNote(StatesGroup):
    waiting_for_text = State()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("Введите текст заметки:")
    await state.set_state(AddNote.waiting_for_text)


@router.message(AddNote.waiting_for_text)
async def add_note_text(message: Message, state: FSMContext):
    from database import add_note
    
    await add_note(message.text)
    await message.answer("✅ Запись добавлена")
    await state.clear()