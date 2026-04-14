import logging

import pytest

import bot
from bot.logging_config import resolve_log_level


class TestResolveLogLevel:
    def test_returns_level_for_valid_value(self):
        level, is_invalid = resolve_log_level("debug")

        assert level == logging.DEBUG
        assert is_invalid is False

    def test_falls_back_for_invalid_value(self):
        level, is_invalid = resolve_log_level("not-a-level")

        assert level == logging.INFO
        assert is_invalid is True


class TestBotStartup:
    @pytest.mark.asyncio
    async def test_main_raises_clear_error_when_bot_token_missing(self, monkeypatch):
        monkeypatch.setattr("config.BOT_TOKEN", None)

        with pytest.raises(Exception, match="Token is invalid"):
            await bot.main()
