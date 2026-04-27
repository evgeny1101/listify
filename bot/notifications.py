from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import ALLOWED_USERS, BOT_TOKEN, NOTIFICATION_TIME
from database import get_notes_count

from .logging_config import logger

scheduler: AsyncIOScheduler | None = None


async def send_notifications() -> None:
    notes_count = await get_notes_count()
    if notes_count == 0:
        logger.info("No notes, skipping notification")
        return

    bot_instance = Bot(token=BOT_TOKEN)
    try:
        for user_id in ALLOWED_USERS:
            try:
                await bot_instance.send_message(
                    user_id,
                    f"📝 У вас {notes_count} заметок. Нажмите /ls чтобы посмотреть.",
                )
                logger.info(f"Notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to {user_id}: {e}")
    finally:
        await bot_instance.session.close()


def start_scheduler() -> None:
    global scheduler
    if NOTIFICATION_TIME is None or NOTIFICATION_TIME == "":
        logger.info("NOTIFICATION_TIME not set, skipping scheduler")
        return

    try:
        hour, minute = map(int, NOTIFICATION_TIME.split(":"))
    except ValueError:
        logger.error(f"Invalid NOTIFICATION_TIME format: {NOTIFICATION_TIME}")
        return

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_notifications,
        "cron",
        hour=hour,
        minute=minute,
    )
    scheduler.start()
    logger.info(f"Notification scheduler started at {NOTIFICATION_TIME}")
