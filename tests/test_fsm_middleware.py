from unittest.mock import AsyncMock, MagicMock

import pytest

from middlewares.fsm_interrupter import FSMInterrupterMiddleware


class TestFSMInterrupterMiddleware:
    @pytest.fixture
    def middleware(self):
        return FSMInterrupterMiddleware()

    @pytest.fixture
    def mock_handler(self):
        handler = AsyncMock()
        handler.return_value = "handler_result"
        return handler

    @pytest.mark.asyncio
    async def test_does_not_interrupt_non_command(self, middleware, mock_handler):
        message = MagicMock()
        message.text = "Just some text"

        state = AsyncMock()
        state.get_state = AsyncMock(return_value="AddNote:waiting_for_text")

        data = {"state": state}

        result = await middleware(mock_handler, message, data)

        mock_handler.assert_called_once_with(message, data)
        state.clear.assert_not_called()
        assert result == "handler_result"

    @pytest.mark.asyncio
    async def test_does_not_interrupt_when_no_fsm_state(self, middleware, mock_handler):
        message = MagicMock()
        message.text = "/start"

        state = AsyncMock()
        state.get_state = AsyncMock(return_value=None)

        data = {"state": state}

        result = await middleware(mock_handler, message, data)

        mock_handler.assert_called_once_with(message, data)
        state.clear.assert_not_called()
        assert result == "handler_result"

    @pytest.mark.asyncio
    async def test_interrupts_command_when_fsm_active(self, middleware, mock_handler):
        message = MagicMock()
        message.text = "/start"

        state = AsyncMock()
        state.get_state = AsyncMock(return_value="AddNote:waiting_for_text")

        data = {"state": state}

        result = await middleware(mock_handler, message, data)

        state.clear.assert_called_once()
        mock_handler.assert_called_once_with(message, data)
        assert result == "handler_result"

    @pytest.mark.asyncio
    async def test_interrupts_various_commands(self, middleware, mock_handler):
        state = AsyncMock()
        state.get_state = AsyncMock(return_value="AddNote:waiting_for_text")
        data = {"state": state}

        commands = ["/start", "/ls", "/help", "/add", "/del"]

        for cmd_text in commands:
            message = MagicMock()
            message.text = cmd_text
            state.clear.reset_mock()

            await middleware(mock_handler, message, data)

            state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_handles_none_text(self, middleware, mock_handler):
        message = MagicMock()
        message.text = None

        state = AsyncMock()
        state.get_state = AsyncMock(return_value="AddNote:waiting_for_text")

        data = {"state": state}

        result = await middleware(mock_handler, message, data)

        state.clear.assert_not_called()
        mock_handler.assert_called_once()
        assert result == "handler_result"

    @pytest.mark.asyncio
    async def test_handles_missing_state_in_data(self, middleware, mock_handler):
        message = MagicMock()
        message.text = "/start"

        data = {}

        result = await middleware(mock_handler, message, data)

        mock_handler.assert_called_once_with(message, data)
        assert result == "handler_result"
