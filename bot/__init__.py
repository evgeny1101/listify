from .run import dp, bot


async def main():
    from handlers.commands import router as commands_router
    from handlers.add import router as add_router
    from handlers.list import router as list_router
    from handlers.delete import router as delete_router
    
    dp.include_router(commands_router)
    dp.include_router(add_router)
    dp.include_router(list_router)
    dp.include_router(delete_router)
    
    from database import init_db
    await init_db()
    
    print("Bot started...")
    await dp.start_polling(bot)