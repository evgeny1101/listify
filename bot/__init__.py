from .run import dp, bot
from .logging_config import logger
from .commands import commands


async def main():
    from handlers.commands import router as commands_router
    from handlers.add import router as add_router
    from handlers.list import router as list_router
    from handlers.delete import router as delete_router

    from middlewares.fsm_interrupter import FSMInterrupterMiddleware
    from middlewares.auto_logging import AutoLoggingMiddleware

    dp.message.middleware(FSMInterrupterMiddleware())
    dp.message.middleware(AutoLoggingMiddleware())

    dp.include_router(commands_router)
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(delete_router)

    from database import init_db

    await init_db()

    await bot.set_my_commands(commands)

    logger.info("Bot started...")
    await dp.start_polling(bot)
