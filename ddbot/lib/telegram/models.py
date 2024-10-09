import dataclasses

import aiogram


@dataclasses.dataclass
class Message:
    text: str
    parse_mode: aiogram.enums.ParseMode


__all__ = [
    "Message",
]
