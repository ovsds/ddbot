import dataclasses
import logging
import typing

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.types as aiogram_types

import lib.character.models as character_models
import lib.character.protocols as character_protocols
import lib.context.models as context_models
import lib.context.protocols as context_protocols
import lib.telegram.context as telegram_context
import lib.utils.cache as cache_utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class CharacterSetCommandHandler:
    context_service: context_protocols.ContextServiceProtocol
    character_service: character_protocols.CharacterServiceProtocol

    async def process(self, message: aiogram.types.Message):
        if message.from_user is None:
            logger.debug("message.from_user is None")
            return

        if message.from_user.is_bot:
            logger.debug("message.from_user.is_bot")
            return

        if message.text is None:
            logger.debug("message.text is None")
            return

        command = self._command.extract_command(message.text)

        if command.args is None:
            await message.reply(text="Usage: /character_set <character_id>")
            return

        try:
            character_id = int(command.args)
        except Exception:
            await message.reply(text=f"Invalid character_id '{command.args}', expected integer")
            return

        try:
            character = await self.character_service.get(character_id)
        except character_protocols.CharacterServiceProtocol.NotFoundError:
            await message.reply(text=f"Character not found: {character_id}")
            return
        except character_protocols.CharacterServiceProtocol.AccessError:
            await message.reply(text=f"Character access error: {character_id}")
            return
        except character_protocols.CharacterServiceProtocol.RepositoryError:
            await message.reply(text=f"Unknown error while fetching character: {character_id}")
            return

        context_key = telegram_context.get_context_key_from_message(message)
        await self.context_service.set(
            key=context_key,
            context=context_models.Context(
                character_id=character.id,
            ),
        )

        await message.reply(text=f"Current character updated: {character.name}")

    @property
    def bot_commands(self) -> typing.Sequence[aiogram_types.BotCommand]:
        return [aiogram_types.BotCommand(command="character_set", description="Set your character")]

    @property
    def _command(self) -> aiogram_filters.Command:
        return aiogram_filters.Command(commands=self.bot_commands)

    @property
    def filters(self) -> typing.Sequence[aiogram_filters.Filter]:
        return [self._command]


@dataclasses.dataclass(frozen=True)
class CharacterCacheClear:
    context_service: context_protocols.ContextServiceProtocol
    cache: cache_utils.CacheProtocol[character_models.Character]

    async def process(self, message: aiogram.types.Message):
        if message.from_user is None:
            logger.debug("message.from_user is None")
            return

        if message.from_user.is_bot:
            logger.debug("message.from_user.is_bot")
            return

        context_key = telegram_context.get_context_key_from_message(message)

        try:
            context = await self.context_service.get(key=context_key)
        except context_protocols.ContextServiceProtocol.NotFoundError:
            await message.reply(text="No character is set")
            return

        await self.cache.clear(str(context.character_id))
        await message.reply(text="Character cache cleared")

    @property
    def bot_commands(self) -> typing.Sequence[aiogram_types.BotCommand]:
        return [aiogram_types.BotCommand(command="character_cache_clear", description="Clear your character cache")]

    @property
    def filters(self) -> typing.Sequence[aiogram_filters.Filter]:
        return [aiogram_filters.Command(commands=self.bot_commands)]


__all__ = [
    "CharacterCacheClear",
    "CharacterSetCommandHandler",
]
