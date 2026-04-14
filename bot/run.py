from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN

bot: Bot | None = Bot(token=BOT_TOKEN) if BOT_TOKEN else None
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
