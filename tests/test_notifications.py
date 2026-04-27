from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestGetNotesCount:
    @pytest.mark.asyncio
    async def test_get_notes_count_returns_count(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_cursor = MagicMock()
            mock_cursor.fetchone = AsyncMock(return_value=[5])

            mock_execute_result = MagicMock()
            mock_execute_result.__aenter__ = AsyncMock(return_value=mock_cursor)
            mock_execute_result.__aexit__ = AsyncMock(return_value=None)

            mock_connection = MagicMock()
            mock_connection.execute = MagicMock(return_value=mock_execute_result)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            from database.db import get_notes_count

            result = await get_notes_count()

            assert result == 5

    @pytest.mark.asyncio
    async def test_get_notes_count_returns_zero_when_empty(self):
        with patch("database.db.aiosqlite") as mock_aiosqlite:
            mock_cursor = MagicMock()
            mock_cursor.fetchone = AsyncMock(return_value=[0])

            mock_execute_result = MagicMock()
            mock_execute_result.__aenter__ = AsyncMock(return_value=mock_cursor)
            mock_execute_result.__aexit__ = AsyncMock(return_value=None)

            mock_connection = MagicMock()
            mock_connection.execute = MagicMock(return_value=mock_execute_result)
            mock_connection.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_connection.__aexit__ = AsyncMock(return_value=None)
            mock_aiosqlite.connect.return_value = mock_connection

            from database.db import get_notes_count

            result = await get_notes_count()

            assert result == 0


class TestSendNotifications:
    @pytest.mark.asyncio
    async def test_send_notifications_sends_to_all_users(self):
        import bot.notifications as notifications_module
        from bot.notifications import send_notifications

        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()
        mock_bot.session.close = AsyncMock()

        async def mock_get_notes_count():
            return 3

        with (
            patch.object(notifications_module, "get_notes_count", mock_get_notes_count),
            patch.object(notifications_module, "BOT_TOKEN", "123456:ABC"),
            patch.object(notifications_module, "ALLOWED_USERS", {123, 456}),
            patch.object(notifications_module, "Bot", return_value=mock_bot),
        ):
            await send_notifications()

            assert mock_bot.send_message.call_count == 2
            mock_bot.send_message.assert_any_call(
                123, "📝 У вас 3 заметок. Нажмите /ls чтобы посмотреть."
            )
            mock_bot.send_message.assert_any_call(
                456, "📝 У вас 3 заметок. Нажмите /ls чтобы посмотреть."
            )

    @pytest.mark.asyncio
    async def test_send_notifications_skips_when_no_notes(self):
        with (
            patch("bot.notifications.get_notes_count") as mock_count,
            patch("bot.notifications.BOT_TOKEN", "123456:ABC"),
            patch("bot.notifications.ALLOWED_USERS", {123}),
            patch("aiogram.Bot") as mock_bot_class,
        ):
            mock_bot = MagicMock()
            mock_bot.send_message = AsyncMock()
            mock_bot.session.close = AsyncMock()
            mock_bot_class.return_value = mock_bot
            mock_count.return_value = 0

            from bot.notifications import send_notifications

            await send_notifications()

            mock_bot.send_message.assert_not_called()


class TestStartScheduler:
    def test_start_scheduler_skips_when_time_not_set(self):
        with (
            patch("bot.notifications.logger") as mock_logger,
            patch("bot.notifications.NOTIFICATION_TIME", None),
            patch("bot.notifications.BOT_TOKEN", "123456:ABC"),
        ):
            from bot.notifications import start_scheduler

            start_scheduler()

            mock_logger.info.assert_called_with(
                "NOTIFICATION_TIME not set, skipping scheduler"
            )

    def test_start_scheduler_skips_when_time_empty(self):
        with (
            patch("bot.notifications.logger") as mock_logger,
            patch("bot.notifications.NOTIFICATION_TIME", ""),
            patch("bot.notifications.BOT_TOKEN", "123456:ABC"),
        ):
            from bot.notifications import start_scheduler

            start_scheduler()

            mock_logger.info.assert_called_with(
                "NOTIFICATION_TIME not set, skipping scheduler"
            )

    def test_start_scheduler_parses_valid_time(self):
        with (
            patch("bot.notifications.logger") as mock_logger,
            patch("bot.notifications.NOTIFICATION_TIME", "17:00"),
            patch("bot.notifications.BOT_TOKEN", "123456:ABC"),
            patch("bot.notifications.AsyncIOScheduler") as mock_scheduler_class,
        ):
            from bot.notifications import start_scheduler

            start_scheduler()

            mock_scheduler_class.assert_called_once()
            mock_logger.info.assert_called_with(
                "Notification scheduler started at 17:00"
            )
