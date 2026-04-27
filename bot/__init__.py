from .commands import commands
from .logging_config import logger


async def main():
    from handlers.add import router as add_router
    from handlers.commands import router as commands_router
    from handlers.delete import router as delete_router
    from handlers.edit import router as edit_router
    from handlers.list import router as list_router
    from middlewares.access_check import AccessCheckMiddleware
    from middlewares.auto_logging import AutoLoggingMiddleware
    from middlewares.fsm_interrupter import FSMInterrupterMiddleware

    from .notifications import start_scheduler
    from .run import bot, dp

    # Middleware order: AccessCheck -> FSMInterrupter -> AutoLogging
    dp.message.middleware(AccessCheckMiddleware())
    dp.message.middleware(FSMInterrupterMiddleware())
    dp.message.middleware(AutoLoggingMiddleware())

    dp.include_router(commands_router)
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(delete_router)
    dp.include_router(edit_router)

    from database import init_db

    await init_db()

    start_scheduler()

    await bot.set_my_commands(commands)

    logger.info("Bot started...")
    await dp.start_polling(bot)
