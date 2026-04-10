from aiogram import BaseMiddleware
from aiogram.types import Message


class FSMInterrupterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        if event.text and event.text.startswith("/"):
            state = data.get("state")
            if state:
                current_state = await state.get_state()
                if current_state:
                    await state.clear()
        return await handler(event, data)
