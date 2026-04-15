from aiogram.types import BotCommand

commands = [
    BotCommand(command="add", description="Добавить запись"),
    BotCommand(command="ls", description="Посмотреть все записи"),
    BotCommand(command="del", description="Удалить запись <id>"),
    BotCommand(command="edit", description="Редактировать запись <id>"),
    BotCommand(command="help", description="Помощь"),
]
