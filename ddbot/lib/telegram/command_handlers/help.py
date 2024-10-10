import dataclasses
import typing

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.types as aiogram_types

DEFAULT_HELP_MESSAGE_TEMPLATE = (
    "General commands:\n"
    "{general_commands}\n"
    "\n"
    "Ability checks:\n"
    "{ability_check_commands}\n"
    "\n"
    "Saving throws:\n"
    "{saving_throw_commands}\n"
    "\n"
    "Skill checks:\n"
    "{skill_check_commands}\n"
    "\n"
    "Miscellaneous checks:\n"
    "{miscellaneous_check_commands}\n"
    "\n"
    "Other commands:\n"
    "{help_command}\n"
    "\n"
    "In case of any issues check the repo: https://github.com/ovsds/ddbot"
)


def render_bot_commands(commands: list[aiogram_types.BotCommand]) -> str:
    return "\n".join(f"  /{command.command} - {command.description}" for command in commands)


def render_help_message(
    template: str,
    general_commands: list[aiogram_types.BotCommand],
    ability_check_commands: list[aiogram_types.BotCommand],
    saving_throw_commands: list[aiogram_types.BotCommand],
    skill_check_commands: list[aiogram_types.BotCommand],
    miscellaneous_check_commands: list[aiogram_types.BotCommand],
    escape_characters: str,
) -> str:
    result = template.format(
        general_commands=render_bot_commands(general_commands),
        ability_check_commands=render_bot_commands(ability_check_commands),
        saving_throw_commands=render_bot_commands(saving_throw_commands),
        skill_check_commands=render_bot_commands(skill_check_commands),
        miscellaneous_check_commands=render_bot_commands(miscellaneous_check_commands),
        help_command=render_bot_commands([aiogram_types.BotCommand(command="help", description="Show this message")]),
    )

    for character in escape_characters:
        result = result.replace(character, f"\\{character}")

    return result


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
    "DEFAULT_HELP_MESSAGE_TEMPLATE",
    "HelpCommandHandler",
    "render_help_message",
]
