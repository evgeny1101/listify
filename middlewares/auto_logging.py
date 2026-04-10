from contextvars import ContextVar
from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.logging_config import logger

COMMANDS = {"/start", "/help", "/add", "/del", "/list"}

user_id_var: ContextVar[int] = ContextVar("user_id", default=None)
command_var: ContextVar[str] = ContextVar("command", default=None)


class AutoLoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.from_user and event.text:
            cmd = event.text.split()[0] if event.text.startswith("/") else None

            if cmd in COMMANDS:
                user_id_var.set(event.from_user.id)
                command_var.set(cmd)

                data["user_id"] = event.from_user.id
                data["command"] = cmd

                logger.info("Command received", user_id=event.from_user.id, command=cmd)

        return await handler(event, data)
