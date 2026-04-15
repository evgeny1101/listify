from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для заметок.\n\n"
        "Доступные команды:\n"
        "/add - добавить запись\n"
        "/ls - посмотреть все записи\n"
        "/edit - редактировать запись\n"
        "/del - удалить запись\n"
        "/help - помощь"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📝 <b>Справка</b>\n\n"
        "/add - добавить новую запись\n"
        "/ls - показать все записи (с индексами)\n"
        "/edit - редактировать запись (можно добавить/заменить изображение)\n"
        "/del - удалить записи (можно несколько через запятую или диапазон)",
        parse_mode="HTML",
    )
