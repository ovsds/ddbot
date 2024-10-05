import logging

import aiogram.types as aiogram_types

logger = logging.getLogger(__name__)


def get_context_key_from_message(message: aiogram_types.Message) -> str:
    if message.from_user is None:
        logger.debug("message.from_user is None")
        raise ValueError("message.from_user is None")

    return f"telegram_{message.from_user.id}_{message.chat.id}"


__all__ = [
    "get_context_key_from_message",
]
