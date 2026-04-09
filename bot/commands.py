from aiogram.types import BotCommand

commands = [
    BotCommand(command="add", description="Добавить запись"),
    BotCommand(command="list", description="Посмотреть все записи"),
    BotCommand(command="del", description="Удалить запись <id>"),
    BotCommand(command="help", description="Помощь"),
]
