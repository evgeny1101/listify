from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

MAX_NOTE_LENGTH = 200


class AddNote(StatesGroup):
    waiting_for_text = State()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    text = parts[1].strip() if len(parts) > 1 else ""

    if text:
        from database import add_note

        truncated = False
        if len(text) > MAX_NOTE_LENGTH:
            text = text[:MAX_NOTE_LENGTH]
            truncated = True

        await add_note(text)
        if truncated:
            await message.answer("⚠️ Запись добавлена (обрезано до 200 символов)")
        else:
            await message.answer("✅ Запись добавлена")
    else:
        await message.answer(f"Введите текст заметки (до {MAX_NOTE_LENGTH} символов):")
        await state.set_state(AddNote.waiting_for_text)


@router.message(AddNote.waiting_for_text)
async def add_note_text(message: Message, state: FSMContext):
    from database import add_note

    text = message.text
    truncated = False
    if len(text) > MAX_NOTE_LENGTH:
        text = text[:MAX_NOTE_LENGTH]
        truncated = True

    await add_note(text)
    if truncated:
        await message.answer("⚠️ Запись добавлена (обрезано до 200 символов)")
    else:
        await message.answer("✅ Запись добавлена")
    await state.clear()
