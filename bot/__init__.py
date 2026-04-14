from .commands import commands
from .logging_config import logger
from .run import bot, dp


async def main():
    if bot is None:
        raise ValueError("BOT_TOKEN is not set. Please set BOT_TOKEN in .env")

    from handlers.add import router as add_router
    from handlers.commands import router as commands_router
    from handlers.delete import router as delete_router
    from handlers.list import router as list_router
    from middlewares.access_check import AccessCheckMiddleware
    from middlewares.auto_logging import AutoLoggingMiddleware
    from middlewares.fsm_interrupter import FSMInterrupterMiddleware

    # Add access check middleware first to reject unauthorized users early
    dp.message.middleware(AccessCheckMiddleware())
    dp.message.middleware(FSMInterrupterMiddleware())
    dp.message.middleware(AutoLoggingMiddleware())

    dp.include_router(commands_router)
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(delete_router)

    from database import init_db

    await init_db()

    assert bot is not None
    await bot.set_my_commands(commands)

    logger.info("Bot started...")
    await dp.start_polling(bot)
