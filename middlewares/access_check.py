from __future__ import annotations

import logging

from aiogram import BaseMiddleware
from aiogram.types import Message

from config import ALLOWED_USERS, ALLOWED_USERS_ACTIVE

logger = logging.getLogger(__name__)


class AccessCheckMiddleware(BaseMiddleware):
    """Middleware to check if user is in allowed list."""

    async def __call__(self, handler, event: Message, data: dict):
        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id

        # If whitelist not configured or empty — block all (protection by default)
        if not ALLOWED_USERS_ACTIVE:
            logger.debug(
                f"Access denied: whitelist not configured, blocking user {user_id}"
            )
            return None

        # Whitelist is configured — check if user is allowed
        if user_id not in ALLOWED_USERS:
            logger.debug(f"Access denied for user {user_id}")
            return None

        return await handler(event, data)
