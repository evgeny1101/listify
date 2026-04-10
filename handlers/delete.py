from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.formatters import format_note_short, send_notes_in_chunks

router = Router()


class DeleteNote(StatesGroup):
    waiting_for_ids = State()


def parse_ids(text: str) -> list[int]:
    parsed = []
    for part in text.split(","):
        part = part.strip()
        if part:
            try:
                parsed.append(int(part))
            except ValueError:
                pass
    return parsed


async def show_delete_confirm(message: Message, ids: list[int], state: FSMContext):
    from database import get_notes
    from keyboards import get_multi_delete_keyboard

    notes = await get_notes()

    valid_ids = [i for i in ids if 1 <= i <= len(notes)]

    if not valid_ids:
        await message.answer("Неверные ID. Введите существующие номера записей.")
        return

    await state.update_data(ids=valid_ids)

    text = "Удалить записи #" + ", ".join(map(str, valid_ids)) + "?"

    await message.answer(text, reply_markup=get_multi_delete_keyboard(valid_ids))


@router.message(Command("del"))
async def cmd_del(message: Message, state: FSMContext):
    from database import get_notes

    parts = message.text.split(maxsplit=1)
    args = parts[1].strip() if len(parts) > 1 else ""

    notes = await get_notes()

    if not notes:
        await message.answer("Записей нет")
        return

    if not args:
        await send_notes_in_chunks(message, notes, format_note_short)
        text = "\nВведите ID (можно несколько через запятую). Пример: 1, 2, 3"
        await message.answer(text)
        await state.set_state(DeleteNote.waiting_for_ids)
        return

    ids = parse_ids(args)

    if not ids:
        await message.answer("ID должны быть числами.\nПример: /del 1, 2, 3")
        return

    await show_delete_confirm(message, ids, state)


@router.message(DeleteNote.waiting_for_ids)
async def on_ids_input(message: Message, state: FSMContext):
    ids = parse_ids(message.text)

    if not ids:
        await message.answer("ID должны быть числами через запятую. Пример: 1, 2, 3")
        return

    await show_delete_confirm(message, ids, state)


@router.callback_query()
async def on_delete_confirm(callback: CallbackQuery, state: FSMContext):
    from database import get_notes, delete_note

    data = callback.data
    action, ids_str = data.split(":")
    ids = list(map(int, ids_str.split(",")))

    if action == "confirm_delete":
        notes = await get_notes()
        deleted = []

        for idx in ids:
            if 1 <= idx <= len(notes):
                note = notes[idx - 1]
                await delete_note(note.id)
                deleted.append(idx)

        if deleted:
            text = "✅ Записи #" + ", ".join(map(str, deleted)) + " удалены"
        else:
            text = "Записи уже удалены"

        await callback.message.edit_text(text, reply_markup=None)
    else:
        await callback.message.edit_text("Удаление отменено", reply_markup=None)

    await callback.answer()
    await state.clear()
