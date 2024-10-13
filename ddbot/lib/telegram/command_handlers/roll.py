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


@dataclasses.dataclass
class AbilityCheckCommand:
    command: str
    description: str
    ability: character_models.CharacterAbility


ABILITY_CHECK_COMMANDS: list[AbilityCheckCommand] = [
    AbilityCheckCommand(
        command="str_check",
        description="Strength check",
        ability=character_models.CharacterAbility.STRENGTH,
    ),
    AbilityCheckCommand(
        command="dex_check",
        description="Dexterity check",
        ability=character_models.CharacterAbility.DEXTERITY,
    ),
    AbilityCheckCommand(
        command="con_check",
        description="Constitution check",
        ability=character_models.CharacterAbility.CONSTITUTION,
    ),
    AbilityCheckCommand(
        command="int_check",
        description="Intelligence check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
    ),
    AbilityCheckCommand(
        command="wis_check",
        description="Wisdom check",
        ability=character_models.CharacterAbility.WISDOM,
    ),
    AbilityCheckCommand(
        command="cha_check",
        description="Charisma check",
        ability=character_models.CharacterAbility.CHARISMA,
    ),
]


@dataclasses.dataclass
class SavingThrowCommand:
    command: str
    description: str
    ability: character_models.CharacterAbility


SAVING_THROW_COMMANDS: list[SavingThrowCommand] = [
    SavingThrowCommand(
        command="str_save",
        description="Strength saving throw",
        ability=character_models.CharacterAbility.STRENGTH,
    ),
    SavingThrowCommand(
        command="dex_save",
        description="Dexterity saving throw",
        ability=character_models.CharacterAbility.DEXTERITY,
    ),
    SavingThrowCommand(
        command="con_save",
        description="Constitution saving throw",
        ability=character_models.CharacterAbility.CONSTITUTION,
    ),
    SavingThrowCommand(
        command="int_save",
        description="Intelligence saving throw",
        ability=character_models.CharacterAbility.INTELLIGENCE,
    ),
    SavingThrowCommand(
        command="wis_save",
        description="Wisdom saving throw",
        ability=character_models.CharacterAbility.WISDOM,
    ),
    SavingThrowCommand(
        command="cha_save",
        description="Charisma saving throw",
        ability=character_models.CharacterAbility.CHARISMA,
    ),
]


@dataclasses.dataclass
class SkillCheckCommand:
    command: str
    description: str
    ability: character_models.CharacterAbility
    skill: character_models.CharacterSkill


SKILL_CHECK_COMMANDS: list[SkillCheckCommand] = [
    SkillCheckCommand(
        command="acrobatics",
        description="Acrobatics check",
        ability=character_models.CharacterAbility.DEXTERITY,
        skill=character_models.CharacterSkill.ACROBATICS,
    ),
    SkillCheckCommand(
        command="animal_handling",
        description="Animal Handling check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.ANIMAL_HANDLING,
    ),
    SkillCheckCommand(
        command="arcana",
        description="Arcana check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.ARCANA,
    ),
    SkillCheckCommand(
        command="athletics",
        description="Athletics check",
        ability=character_models.CharacterAbility.STRENGTH,
        skill=character_models.CharacterSkill.ATHLETICS,
    ),
    SkillCheckCommand(
        command="deception",
        description="Deception check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.DECEPTION,
    ),
    SkillCheckCommand(
        command="history",
        description="History check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.HISTORY,
    ),
    SkillCheckCommand(
        command="insight",
        description="Insight check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.INSIGHT,
    ),
    SkillCheckCommand(
        command="intimidation",
        description="Intimidation check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.INTIMIDATION,
    ),
    SkillCheckCommand(
        command="investigation",
        description="Investigation check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.INVESTIGATION,
    ),
    SkillCheckCommand(
        command="medicine",
        description="Medicine check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.MEDICINE,
    ),
    SkillCheckCommand(
        command="nature",
        description="Nature check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.NATURE,
    ),
    SkillCheckCommand(
        command="perception",
        description="Perception check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.PERCEPTION,
    ),
    SkillCheckCommand(
        command="performance",
        description="Performance check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.PERFORMANCE,
    ),
    SkillCheckCommand(
        command="persuasion",
        description="Persuasion check",
        ability=character_models.CharacterAbility.CHARISMA,
        skill=character_models.CharacterSkill.PERSUASION,
    ),
    SkillCheckCommand(
        command="religion",
        description="Religion check",
        ability=character_models.CharacterAbility.INTELLIGENCE,
        skill=character_models.CharacterSkill.RELIGION,
    ),
    SkillCheckCommand(
        command="sleight_of_hand",
        description="Sleight of Hand check",
        ability=character_models.CharacterAbility.DEXTERITY,
        skill=character_models.CharacterSkill.SLEIGHT_OF_HAND,
    ),
    SkillCheckCommand(
        command="stealth",
        description="Stealth check",
        ability=character_models.CharacterAbility.DEXTERITY,
        skill=character_models.CharacterSkill.STEALTH,
    ),
    SkillCheckCommand(
        command="survival",
        description="Survival check",
        ability=character_models.CharacterAbility.WISDOM,
        skill=character_models.CharacterSkill.SURVIVAL,
    ),
]


class InitiativeCommand:
    command = "initiative"
    description = "Initiative check"


INITIATIVE_COMMAND = InitiativeCommand()


class DeathSavingThrowCommand:
    command = "death_save"
    description = "Death saving throw"


DEATH_SAVING_THROW_COMMAND = DeathSavingThrowCommand()


@dataclasses.dataclass(frozen=True)
class RollCommandHandler:
    context_service: context_protocols.ContextServiceProtocol
    character_service: character_protocols.CharacterServiceProtocol
    roll_callback: character_protocols.RollCallbackProtocol

    command: str
    description: str

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

        roll_result = await self.roll_callback(character)

        await message.reply(telegram_messages.ROLL_RESULT.format(details=roll_result.details, value=roll_result.value))

    @property
    def bot_commands(self) -> typing.Sequence[aiogram_types.BotCommand]:
        return [
            aiogram_types.BotCommand(
                command=self.command,
                description=self.description,
            )
        ]

    @property
    def _command(self) -> aiogram_filters.Command:
        return aiogram_filters.Command(commands=self.bot_commands)

    @property
    def filters(self) -> typing.Sequence[aiogram_filters.Filter]:
        return [self._command]


__all__ = [
    "ABILITY_CHECK_COMMANDS",
    "DEATH_SAVING_THROW_COMMAND",
    "INITIATIVE_COMMAND",
    "RollCommandHandler",
    "SAVING_THROW_COMMANDS",
    "SKILL_CHECK_COMMANDS",
]
