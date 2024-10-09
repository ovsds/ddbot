import dataclasses
import typing

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.types as aiogram_types


@dataclasses.dataclass(frozen=True)
class HelpCommandHandler:
    text: str
    parse_mode = aiogram.enums.ParseMode.MARKDOWN_V2

    async def process(self, message: aiogram.types.Message):
        await message.answer(self.text, parse_mode=self.parse_mode)

    @property
    def bot_commands(self) -> typing.Sequence[aiogram_types.BotCommand]:
        return [
            aiogram_types.BotCommand(command="help", description="Show help message"),
            aiogram_types.BotCommand(command="start", description="Start the bot"),
        ]

    @property
    def filters(self) -> typing.Sequence[aiogram_filters.Filter]:
        return [aiogram_filters.Command(commands=self.bot_commands)]


__all__ = [
    "HelpCommandHandler",
]
