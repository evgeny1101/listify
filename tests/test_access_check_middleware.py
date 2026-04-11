from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from middlewares.access_check import AccessCheckMiddleware


class TestAccessCheckMiddleware:
    @pytest.fixture
    def middleware(self):
        return AccessCheckMiddleware()

    @pytest.fixture
    def mock_handler(self):
        handler = AsyncMock()
        handler.return_value = "handler_result"
        return handler

    @pytest.mark.asyncio
    async def test_blocks_all_when_whitelist_not_configured(
        self, middleware, mock_handler
    ):
        with patch("middlewares.access_check.ALLOWED_USERS_ACTIVE", False):
            message = MagicMock()
            message.from_user = MagicMock()
            message.from_user.id = 123

            result = await middleware(mock_handler, message, {})

            mock_handler.assert_not_called()
            assert result is None

    @pytest.mark.asyncio
    async def test_allows_user_when_in_whitelist(self, middleware, mock_handler):
        with (
            patch("middlewares.access_check.ALLOWED_USERS_ACTIVE", True),
            patch("middlewares.access_check.ALLOWED_USERS", {123, 456}),
        ):
            message = MagicMock()
            message.from_user = MagicMock()
            message.from_user.id = 123

            result = await middleware(mock_handler, message, {})

            mock_handler.assert_called_once_with(message, {})
            assert result == "handler_result"

    @pytest.mark.asyncio
    async def test_blocks_user_when_not_in_whitelist(self, middleware, mock_handler):
        with (
            patch("middlewares.access_check.ALLOWED_USERS_ACTIVE", True),
            patch("middlewares.access_check.ALLOWED_USERS", {123, 456}),
        ):
            message = MagicMock()
            message.from_user = MagicMock()
            message.from_user.id = 999

            result = await middleware(mock_handler, message, {})

            mock_handler.assert_not_called()
            assert result is None

    @pytest.mark.asyncio
    async def test_passes_through_when_no_from_user(self, middleware, mock_handler):
        message = MagicMock()
        message.from_user = None

        result = await middleware(mock_handler, message, {})

        mock_handler.assert_called_once_with(message, {})
        assert result == "handler_result"
