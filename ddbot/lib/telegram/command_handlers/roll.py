import dataclasses
import logging
import typing

import aiogram
import aiogram.filters as aiogram_filters
import aiogram.types as aiogram_types

import lib.character.models as character_models
import lib.character.protocols as character_protocols
import lib.context.protocols as context_protocols
import lib.telegram.context as telegram_context
import lib.telegram.messages as telegram_messages

logger = logging.getLogger(__name__)


class RollCallbackProtocol(typing.Protocol):
    def __call__(self, character: character_models.Character) -> typing.Awaitable[character_models.RollResult]: ...


@dataclasses.dataclass(frozen=True)
class RollCommand:
    command: str
    description: str
    callback: RollCallbackProtocol


@dataclasses.dataclass(frozen=True)
class RollCommandFactory:
    command: str
    description: str

    def make(self, callback: RollCallbackProtocol) -> RollCommand:
        return RollCommand(
            command=self.command,
            description=self.description,
            callback=callback,
        )


class AbilityCallbackProtocol(typing.Protocol):
    async def __call__(
        self, character: character_models.Character, ability: character_models.CharacterAbility
    ) -> character_models.RollResult: ...


@dataclasses.dataclass(frozen=True)
class AbilityCommandFactory:
    command: str
    description: str
    ability: character_models.CharacterAbility

    def make(self, callback: AbilityCallbackProtocol) -> RollCommand:
        async def wrapped_callback(character: character_models.Character) -> character_models.RollResult:
            return await callback(character, self.ability)

        return RollCommand(
            command=self.command,
            description=self.description,
            callback=wrapped_callback,
        )


ABILITY_CHECK_COMMAND_FACTORIES: list[AbilityCommandFactory] = [
    AbilityCommandFactory(
        command="str_check",
        description="Strength check",
        ability=character_models.CharacterAbility.STRENGTH,
    ),
    AbilityCommandFactory(
        command="dex_check",
        description="Dexterity check",
        ability=character_models.CharacterAbility.DEXTERITY,
    ),
    AbilityCommandFactory(
        command="con_check",
        description="Constitution check",
        ability=character_models.CharacterAbility.CONSTITUTION,
    ),
    AbilityCommandFactory(
        command="int_check",
        description="Intelligence check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
    ),
    AbilityCommandFactory(
        command="wis_check",
        description="Wisdom check",
        ability=character_models.CharacterAbility.WISDOM,
    ),
    AbilityCommandFactory(
        command="cha_check",
        description="Charisma check",
        ability=character_models.CharacterAbility.CHARISMA,
    ),
]

ABILITY_SAVE_COMMAND_FACTORIES: list[AbilityCommandFactory] = [
    AbilityCommandFactory(
        command="str_save",
        description="Strength saving throw",
        ability=character_models.CharacterAbility.STRENGTH,
    ),
    AbilityCommandFactory(
        command="dex_save",
        description="Dexterity saving throw",
        ability=character_models.CharacterAbility.DEXTERITY,
    ),
    AbilityCommandFactory(
        command="con_save",
        description="Constitution saving throw",
        ability=character_models.CharacterAbility.CONSTITUTION,
    ),
    AbilityCommandFactory(
        command="int_save",
        description="Intelligence saving throw",
        ability=character_models.CharacterAbility.INTELLIGENCE,
    ),
    AbilityCommandFactory(
        command="wis_save",
        description="Wisdom saving throw",
        ability=character_models.CharacterAbility.WISDOM,
    ),
    AbilityCommandFactory(
        command="cha_save",
        description="Charisma saving throw",
        ability=character_models.CharacterAbility.CHARISMA,
    ),
]


class SkillCallbackProtocol(typing.Protocol):
    async def __call__(
        self,
        character: character_models.Character,
        ability: character_models.CharacterAbility,
        skill: character_models.CharacterSkill,
    ) -> character_models.RollResult: ...


@dataclasses.dataclass(frozen=True)
class SkillCommandFactory:
    command: str
    description: str
    ability: character_models.CharacterAbility
    skill: character_models.CharacterSkill

    def make(self, callback: SkillCallbackProtocol) -> RollCommand:
        async def wrapped_callback(character: character_models.Character) -> character_models.RollResult:
            return await callback(character, self.ability, self.skill)

        return RollCommand(
            command=self.command,
            description=self.description,
            callback=wrapped_callback,
        )


SKILL_CHECK_COMMAND_FACTORIES: list[SkillCommandFactory] = [
    SkillCommandFactory(
        command="acrobatics",
        description="Acrobatics check",
        ability=character_models.CharacterAbility.DEXTERITY,
        skill=character_models.CharacterSkill.ACROBATICS,
    ),
    SkillCommandFactory(
        command="animal_handling",
        description="Animal Handling check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.ANIMAL_HANDLING,
    ),
    SkillCommandFactory(
        command="arcana",
        description="Arcana check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.ARCANA,
    ),
    SkillCommandFactory(
        command="athletics",
        description="Athletics check",
        ability=character_models.CharacterAbility.STRENGTH,
        skill=character_models.CharacterSkill.ATHLETICS,
    ),
    SkillCommandFactory(
        command="deception",
        description="Deception check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.DECEPTION,
    ),
    SkillCommandFactory(
        command="history",
        description="History check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.HISTORY,
    ),
    SkillCommandFactory(
        command="insight",
        description="Insight check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.INSIGHT,
    ),
    SkillCommandFactory(
        command="intimidation",
        description="Intimidation check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.INTIMIDATION,
    ),
    SkillCommandFactory(
        command="investigation",
        description="Investigation check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.INVESTIGATION,
    ),
    SkillCommandFactory(
        command="medicine",
        description="Medicine check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.MEDICINE,
    ),
    SkillCommandFactory(
        command="nature",
        description="Nature check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.NATURE,
    ),
    SkillCommandFactory(
        command="perception",
        description="Perception check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.PERCEPTION,
    ),
    SkillCommandFactory(
        command="performance",
        description="Performance check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.PERFORMANCE,
    ),
    SkillCommandFactory(
        command="persuasion",
        description="Persuasion check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.PERSUASION,
    ),
    SkillCommandFactory(
        command="religion",
        description="Religion check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.RELIGION,
    ),
    SkillCommandFactory(
        command="sleight_of_hand",
        description="Sleight of Hand check",
        ability=character_models.CharacterAbility.DEXTERITY,
        skill=character_models.CharacterSkill.SLEIGHT_OF_HAND,
    ),
    SkillCommandFactory(
        command="stealth",
        description="Stealth check",
        ability=character_models.CharacterAbility.DEXTERITY,
        skill=character_models.CharacterSkill.STEALTH,
    ),
    SkillCommandFactory(
        command="survival",
        description="Survival check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.SURVIVAL,
    ),
]


INITIATIVE_COMMAND_FACTORY = RollCommandFactory(
    command="initiative",
    description="Initiative check",
)

DEATH_SAVE_COMMAND_FACTORY = RollCommandFactory(
    command="death_save",
    description="Death saving throw",
)


@dataclasses.dataclass(frozen=True)
class RollCommandHandler:
    context_service: context_protocols.ContextServiceProtocol
    character_service: character_protocols.CharacterServiceProtocol
    command: RollCommand

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

        context_key = telegram_context.get_context_key_from_message(message)
        try:
            context = await self.context_service.get(key=context_key)
        except context_protocols.ContextServiceProtocol.NotFoundError:
            await message.reply(
                telegram_messages.CHARACTER_FETCH_NOT_SET,
                parse_mode=aiogram.enums.ParseMode.MARKDOWN_V2,
            )
            return

        character_id = context.character_id
        try:
            character = await self.character_service.get(entity_id=character_id)
        except character_protocols.CharacterServiceProtocol.NotFoundError:
            await message.reply(text=telegram_messages.CHARACTER_FETCH_NOT_FOUND.format(character_id=character_id))
            return
        except character_protocols.CharacterServiceProtocol.AccessError:
            await message.reply(text=telegram_messages.CHARACTER_FETCH_NO_ACCESS.format(character_id=character_id))
            return
        except character_protocols.CharacterServiceProtocol.RepositoryError:
            await message.reply(text=telegram_messages.CHARACTER_FETCH_UNKNOWN_ERROR.format(character_id=character_id))
            return

        roll_result = await self.command.callback(character)

        await message.reply(telegram_messages.ROLL_RESULT.format(details=roll_result.details, value=roll_result.value))

    @property
    def bot_commands(self) -> typing.Sequence[aiogram_types.BotCommand]:
        return [
            aiogram_types.BotCommand(
                command=self.command.command,
                description=self.command.description,
            )
        ]

    @property
    def _command(self) -> aiogram_filters.Command:
        return aiogram_filters.Command(commands=self.bot_commands)

    @property
    def filters(self) -> typing.Sequence[aiogram_filters.Filter]:
        return [self._command]


__all__ = [
    "ABILITY_CHECK_COMMAND_FACTORIES",
    "ABILITY_SAVE_COMMAND_FACTORIES",
    "DEATH_SAVE_COMMAND_FACTORY",
    "INITIATIVE_COMMAND_FACTORY",
    "RollCommandHandler",
    "SKILL_CHECK_COMMAND_FACTORIES",
]
