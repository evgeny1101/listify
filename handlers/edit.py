from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database import add_note_image, get_note_images, get_notes, update_note
from handlers.add import (
    get_photo_file_ids,
    has_unsupported_content,
    truncate_text,
)
from keyboards import get_cancel_keyboard

router = Router()


class EditNote(StatesGroup):
    waiting_for_id = State()
    waiting_for_content = State()


async def send_current_note(message: Message, note_index: int) -> None:
    notes = await get_notes()

    if not (1 <= note_index <= len(notes)):
        await message.answer("Запись не найдена")
        return

    note = notes[note_index - 1]
    images = await get_note_images(note.id) if note.has_image else []

    from bot.formatters import send_note_short_with_image

    await send_note_short_with_image(message, note_index, note.text, images)

    await message.answer("Введите новый текст или отправьте изображение:")


@router.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    await state.clear()

    if has_unsupported_content(message):
        await message.answer("⚠️ Поддерживаются только текст и изображения")
        return

    parts = message.text.split(maxsplit=1)
    args = parts[1].strip() if len(parts) > 1 else ""

    notes = await get_notes()

    if not notes:
        await message.answer("Записей нет")
        return

    if not args:
        text = "Введите ID записи для редактирования:"
        await message.answer(text, reply_markup=get_cancel_keyboard())
        await state.set_state(EditNote.waiting_for_id)
        return

    try:
        note_index = int(args)
    except ValueError:
        await message.answer("ID должен быть числом")
        return

    if not (1 <= note_index <= len(notes)):
        await message.answer("Запись не найдена")
        return

    await state.update_data(note_index=note_index, note_db_id=notes[note_index - 1].id)
    await send_current_note(message, note_index)
    await state.set_state(EditNote.waiting_for_content)


@router.message(EditNote.waiting_for_id)
async def edit_note_id(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""

    if text.startswith("/"):
        await state.clear()

        if text == "/del":
            from handlers.delete import cmd_del

            await cmd_del(message, state)
            return

        return

    notes = await get_notes()

    if not text:
        await message.answer("Введите ID записи")
        return

    try:
        note_index = int(text)
    except ValueError:
        await message.answer("ID должен быть числом")
        return

    if not (1 <= note_index <= len(notes)):
        await message.answer("Запись не найдена")
        return

    await state.update_data(note_index=note_index, note_db_id=notes[note_index - 1].id)
    await send_current_note(message, note_index)
    await state.set_state(EditNote.waiting_for_content)


async def process_edit_text(message: Message, state: FSMContext, new_text: str) -> None:
    data = await state.get_data()
    note_db_id = data["note_db_id"]

    new_text, truncated = truncate_text(new_text) if new_text else ("", False)

    await update_note(note_db_id, new_text)

    parts = []
    if truncated:
        parts.append("⚠️ Запись обновлена (обрезано до 200 символов)")
    else:
        parts.append("✅ Запись обновлена")

    await message.answer("".join(parts))
    await state.clear()


async def process_edit_photo(
    message: Message, state: FSMContext, new_text: str
) -> None:
    data = await state.get_data()
    note_db_id = data["note_db_id"]

    large_and_small = get_photo_file_ids(message)

    if not large_and_small:
        await message.answer("⚠️ Не удалось получить изображение")
        return

    if len(list(message.photo)) > 2:
        warning = "⚠️ Можно добавить только первое изображение\n"
    else:
        warning = ""

    small_id, large_id = large_and_small
    caption = message.caption.strip() if message.caption else ""
    if caption.startswith("/"):
        caption = ""

    text = new_text or caption
    text, truncated = truncate_text(text) if text else ("", False)

    await update_note(note_db_id, text if text else "📷 Изображение")

    await add_note_image(note_db_id, "small", small_id)
    await add_note_image(note_db_id, "large", large_id)

    parts = []
    if warning:
        parts.append(warning)
    if text:
        if truncated:
            parts.append("⚠️ Запись обновлена (обрезано до 200 символов)")
        else:
            parts.append("✅ Запись обновлена")
    else:
        parts.append("✅ Изображение обновлено")

    await message.answer("".join(parts))
    await state.clear()


@router.message(EditNote.waiting_for_content)
async def edit_note_content(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    text_or_none = message.text

    if text_or_none and text.startswith("/"):
        await state.clear()
        return

    if message.photo:
        await process_edit_photo(message, state, text)
        return

    if not text:
        await message.answer("⚠️ Введите текст заметки")
        return

    await process_edit_text(message, state, text)


@router.callback_query(F.data == "cancel:edit")
async def on_cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Редактирование отменено")
    await callback.answer()
    await state.clear()
