from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_note, add_note_image
from keyboards import get_cancel_keyboard

router = Router()

MAX_NOTE_LENGTH = 200


def truncate_text(text: str) -> tuple[str, bool]:
    if len(text) > MAX_NOTE_LENGTH:
        return text[:MAX_NOTE_LENGTH], True
    return text, False


def get_photo_file_ids(message: Message) -> tuple[str, str] | None:
    if not message.photo:
        return None
    photos = list(message.photo)
    if len(photos) < 2:
        return None, photos[0].file_id
    return photos[0].file_id, photos[-1].file_id


def has_unsupported_content(message: Message) -> bool:
    return any(
        [
            message.video,
            message.document,
            message.voice,
            message.audio,
            message.sticker,
            message.animation,
        ]
    )


class AddNote(StatesGroup):
    waiting_for_content = State()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if has_unsupported_content(message):
        await message.answer("⚠️ Поддерживаются только текст и изображения")
        return

    parts = message.text.split(maxsplit=1)
    args_text = parts[1].strip() if len(parts) > 1 else ""

    if message.photo:
        await _process_photo(message, state, from_command=True, args_text=args_text)
        return

    if args_text:
        args_text, truncated = truncate_text(args_text)
        await add_note(args_text)
        if truncated:
            await message.answer("⚠️ Запись добавлена (обрезано до 200 символов)")
        else:
            await message.answer("✅ Запись добавлена")
    else:
        await message.answer(
            "Введите текст или отправьте изображение:",
            reply_markup=get_cancel_keyboard(),
        )
        await state.set_state(AddNote.waiting_for_content)


async def _process_photo(
    message: Message, state: FSMContext, from_command: bool = False, args_text: str = ""
):
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
    text = args_text or caption
    text, truncated = truncate_text(text) if text else ("", False)

    note_id = await add_note(text) if text else await add_note("📷 Изображение")

    await add_note_image(note_id, "small", small_id)
    await add_note_image(note_id, "large", large_id)

    parts = []
    if warning:
        parts.append(warning)
    if text:
        if truncated:
            parts.append("⚠️ Запись добавлена (обрезано до 200 символов)")
        else:
            parts.append("✅ Запись добавлена")
    else:
        parts.append("✅ Изображение добавлено")

    await message.answer("".join(parts))


async def _process_text(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if not text:
        await message.answer("⚠️ Введите текст заметки")
        return

    if has_unsupported_content(message):
        await message.answer("⚠️ Поддерживаются только текст и изображения")
        return

    text, truncated = truncate_text(text)
    await add_note(text)
    if truncated:
        await message.answer("⚠️ Запись добавлена (обрезано до 200 символов)")
    else:
        await message.answer("✅ Запись добавлена")
    await state.clear()


@router.message(AddNote.waiting_for_content)
async def add_note_content(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""

    if text.startswith("/"):
        await state.clear()

        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1].strip() if len(parts) > 1 else ""

        if command == "/add" and args:
            await cmd_add(message, type("obj", (), {"text": args, "photo": None})())
            return

        if command == "/del" and args:
            from handlers.delete import parse_ids, show_delete_confirm

            ids = parse_ids(args)
            if ids:
                await show_delete_confirm(message, ids, state)
                return

        if command == "/list":
            from handlers.list import cmd_list

            await cmd_list(message)
            return

        if command == "/start":
            from handlers.commands import cmd_start

            await cmd_start(message)
            return

        if command == "/help":
            from handlers.commands import cmd_help

            await cmd_help(message)
            return

        if command == "/del":
            from handlers.delete import cmd_del

            await cmd_del(message, state)
            return

        await message.answer("❌ Операция прервана. Введите команду заново.")
        return

    if message.photo:
        await _process_photo(message, state)
        return

    await _process_text(message, state)


@router.callback_query(F.data == "cancel_add")
async def on_cancel_input(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Ввод заметки отменён")
    await callback.answer()
    await state.clear()
