from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для заметок.\n\n"
        "Доступные команды:\n"
        "/add - добавить запись\n"
        "/list - посмотреть все записи\n"
        "/del - удалить запись\n"
        "/help - помощь"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📝 <b>Справка</b>\n\n"
        "/add - добавить новую запись\n"
        "/list - показать все записи (с индексами)\n"
        "/del - удалить записи (можно несколько через запятую)",
        parse_mode="HTML",
    )
