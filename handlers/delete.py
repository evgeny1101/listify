from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

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

    from database import get_notes

    notes = await get_notes()

    if not notes:
        await message.answer("Записей нет")
        return

    if index < 1 or index > len(notes):
        await message.answer(f"Неверный индекс. Введите от 1 до {len(notes)}")
        return

    from keyboards import get_delete_confirm_keyboard

    await message.answer(
        f"Удалить заметку #{index}?", reply_markup=get_delete_confirm_keyboard(index)
    )


@router.callback_query()
async def on_delete_confirm(callback: CallbackQuery):
    from database import get_notes, delete_note

    data = callback.data
    action, index_str = data.split(":")
    index = int(index_str)

    if action == "confirm_delete":
        notes = await get_notes()
        if 1 <= index <= len(notes):
            note = notes[index - 1]
            await delete_note(note.id)
            await callback.message.edit_text(
                f"✅ Запись #{index} удалена", reply_markup=None
            )
        else:
            await callback.message.edit_text(
                f"Запись #{index} уже удалена", reply_markup=None
            )
    else:
        await callback.message.edit_text(
            f"Запись #{index} сохранена", reply_markup=None
        )

    await callback.answer()
