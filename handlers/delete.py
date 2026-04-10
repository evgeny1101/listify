from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import delete_note, get_note_images, get_notes
from keyboards import get_multi_delete_keyboard

router = Router()


class DeleteNote(StatesGroup):
    waiting_for_ids = State()


MAX_ID = 10000
MAX_RANGE = 100
MAX_TOTAL = 500


def parse_ids(text: str) -> list[int] | None:
    parsed = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            range_parts = [p.strip() for p in part.split("-") if p.strip()]
            if len(range_parts) == 2:
                try:
                    start, end = int(range_parts[0]), int(range_parts[1])
                    if start > end:
                        start, end = end, start
                    if start > MAX_ID:
                        start = MAX_ID
                    if end > MAX_ID:
                        end = MAX_ID
                    range_size = end - start + 1
                    if range_size > MAX_RANGE:
                        return None
                    parsed.extend(range(start, end + 1))
                except ValueError:
                    pass
        else:
            try:
                num = int(part)
                if num <= MAX_ID:
                    parsed.append(num)
            except ValueError:
                pass
    if len(parsed) > MAX_TOTAL:
        return None
    return parsed[:MAX_TOTAL]


async def show_delete_confirm(message: Message, ids: list[int], state: FSMContext) -> None:
    notes = await get_notes()

    valid_ids = list(dict.fromkeys([i for i in ids if 1 <= i <= len(notes)]))

    if not valid_ids:
        await message.answer("Неверные ID. Введите существующие номера записей.")
        return

    await state.update_data(ids=valid_ids)

    from bot.formatters import send_note_short_with_image

    for idx in valid_ids:
        if 1 <= idx <= len(notes):
            note = notes[idx - 1]
            images = await get_note_images(note.id) if note.has_image else []
            await send_note_short_with_image(message, idx, note.text, images)

    text = "Удалить записи #" + ", ".join(map(str, valid_ids)) + "?"
    await message.answer(text, reply_markup=get_multi_delete_keyboard(valid_ids))


@router.message(Command("del"))
async def cmd_del(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    args = parts[1].strip() if len(parts) > 1 else ""

    notes = await get_notes()

    if not notes:
        await message.answer("Записей нет")
        return

    if not args:
        from bot.formatters import send_note_short_with_image

        for i, note in enumerate(notes, 1):
            images = await get_note_images(note.id) if note.has_image else []
            await send_note_short_with_image(message, i, note.text, images)

        text = "\nВведите ID (можно несколько через запятую или диапазон). Пример: 1, 2-3, 5"
        await message.answer(text)
        await state.set_state(DeleteNote.waiting_for_ids)
        return

    ids = parse_ids(args)

    if ids is None:
        await message.answer(
            f"Слишком много ID (макс. {MAX_TOTAL}) или слишком большой диапазон (макс. {MAX_RANGE})."
        )
        return
    if not ids:
        await message.answer(
            "ID должны быть числами или диапазоном.\nПример: /del 1, 2-3, 5"
        )
        return

    await show_delete_confirm(message, ids, state)


@router.message(DeleteNote.waiting_for_ids)
async def on_ids_input(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""

    if text.startswith("/"):
        await state.clear()

        parts = text.split(maxsplit=1)
        command = parts[0]

        if command == "/del" and len(parts) > 1 and parts[1].strip():
            ids = parse_ids(parts[1])
            if ids:
                await show_delete_confirm(message, ids, state)
                return
            if ids is None:
                await message.answer(
                    f"Слишком много ID (макс. {MAX_TOTAL}) или слишком большой диапазон (макс. {MAX_RANGE})."
                )
                return

        await message.answer("❌ Операция прервана. Введите команду заново.")
        return

    ids = parse_ids(text)

    if ids is None:
        await message.answer(
            f"Слишком много ID (макс. {MAX_TOTAL}) или слишком большой диапазон (макс. {MAX_RANGE})."
        )
        return
    if not ids:
        await message.answer("ID должны быть числами или диапазоном. Пример: 1, 2-3, 5")
        return

    await show_delete_confirm(message, ids, state)


@router.callback_query()
async def on_delete_confirm(callback: CallbackQuery, state: FSMContext):
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
