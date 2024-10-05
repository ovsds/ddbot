import dataclasses
import enum
import itertools
import logging
import typing

import aiohttp
import pydantic

import lib.character.models as models
import lib.character.protocols as protocols

logger = logging.getLogger(__name__)


class Response(pydantic.BaseModel):
    id: int
    success: bool
    message: str
    raw_data: dict[str, typing.Any] = pydantic.Field(alias="data")


class ErrorData(pydantic.BaseModel):
    server_message: str = pydantic.Field(alias="serverMessage")
    error_code: str = pydantic.Field(alias="errorCode")


class StatId(enum.Enum):
    STR = 1
    DEX = 2
    CON = 3
    INT = 4
    WIS = 5
    CHA = 6


class CharacterData(pydantic.BaseModel):
    class ToDataclassError(Exception): ...

    class StatValue(pydantic.BaseModel):
        id: StatId
        value: int

    class OptionalStatValue(pydantic.BaseModel):
        id: StatId
        value: int | None

    class Class(pydantic.BaseModel):
        level: int

    class Modifiers(pydantic.BaseModel):
        class Type(enum.Enum):
            BONUS = "bonus"
            PROFICIENCY = "proficiency"
            EXPERTISE = "expertise"

        class SubType(enum.Enum):
            # Bonus
            STR_SCORE = "strength-score"
            DEX_SCORE = "dexterity-score"
            CON_SCORE = "constitution-score"
            INT_SCORE = "intelligence-score"
            WIS_SCORE = "wisdom-score"
            CHA_SCORE = "charisma-score"

            STR_SAVING_THROW = "strength-saving-throws"
            DEX_SAVING_THROW = "dexterity-saving-throws"
            CON_SAVING_THROW = "constitution-saving-throws"
            INT_SAVING_THROW = "intelligence-saving-throws"
            WIS_SAVING_THROW = "wisdom-saving-throws"
            CHA_SAVING_THROW = "charisma-saving-throws"

            ATHLETICS_SKILL = "athletics"
            ACROBATICS_SKILL = "acrobatics"
            SLEIGHT_OF_HAND_SKILL = "sleight-of-hand"
            STEALTH_SKILL = "stealth"
            ARCANA_SKILL = "arcana"
            HISTORY_SKILL = "history"
            INVESTIGATION_SKILL = "investigation"
            NATURE_SKILL = "nature"
            RELIGION_SKILL = "religion"
            ANIMAL_HANDLING_SKILL = "animal-handling"
            INSIGHT_SKILL = "insight"
            MEDICINE_SKILL = "medicine"
            PERCEPTION_SKILL = "perception"
            SURVIVAL_SKILL = "survival"
            DECEPTION_SKILL = "deception"
            INTIMIDATION_SKILL = "intimidation"
            PERFORMANCE_SKILL = "performance"
            PERSUASION_SKILL = "persuasion"

        class Modifier(pydantic.BaseModel):
            type: str
            sub_type: str = pydantic.Field(alias="subType")
            value: int | None

            friendly_type_name: str = pydantic.Field(alias="friendlyTypeName")
            friendly_subtype_name: str = pydantic.Field(alias="friendlySubtypeName")

        race: list[Modifier]
        class_: list[Modifier] = pydantic.Field(alias="class")
        background: list[Modifier]
        item: list[Modifier]
        feat: list[Modifier]

        @property
        def all_modifiers(self) -> typing.Iterable[Modifier]:
            return itertools.chain(self.race, self.class_, self.background, self.item, self.feat)

        @property
        def all_known_modifiers(self) -> typing.Iterable[Modifier]:
            for modifier in self.all_modifiers:
                if modifier.type not in self.Type:
                    logger.debug(
                        "Unknown modifier type: type(%s), name(%s)",
                        modifier.type,
                        modifier.friendly_type_name,
                    )
                    continue

                if modifier.sub_type not in self.SubType:
                    logger.debug(
                        "Unknown modifier sub type: sub_type(%s), name(%s)",
                        modifier.sub_type,
                        modifier.friendly_subtype_name,
                    )
                    continue

                yield modifier

    id: int
    name: str
    stats: list[StatValue]
    bonus_stats: list[OptionalStatValue] = pydantic.Field(alias="bonusStats")
    override_stats: list[OptionalStatValue] = pydantic.Field(alias="overrideStats")
    classes: list[Class]
    modifiers: Modifiers

    _known_modifiers: list[Modifiers.Modifier] | None = pydantic.PrivateAttr(default=None)

    @property
    def known_modifiers(self) -> list[Modifiers.Modifier]:
        if self._known_modifiers is None:
            self._known_modifiers = list(self.modifiers.all_known_modifiers)

        return self._known_modifiers

    def _get_filtered_modifiers(
        self,
        type_: Modifiers.Type,
        sub_type: Modifiers.SubType,
    ) -> typing.Iterable[Modifiers.Modifier]:
        for modifier in self.known_modifiers:
            if modifier.type == type_.value and modifier.sub_type == sub_type.value:
                yield modifier

    def _get_total_level(self) -> int:
        return sum(cls.level for cls in self.classes)

    def _get_proficiency_bonus(self) -> int:
        total_level = self._get_total_level()

        if total_level < 5:
            return 2
        if total_level < 9:
            return 3
        if total_level < 13:
            return 4
        if total_level < 17:
            return 5

        return 6

    def _get_stat_base_value(self, stat_id: StatId) -> int:
        for stat in self.stats:
            if stat.id == stat_id:
                return stat.value

        raise self.ToDataclassError(f"Stat {stat_id} not found")

    def _get_stat_bonus_value(self, stat_id: StatId) -> int:
        for stat in self.bonus_stats:
            if stat.id == stat_id:
                return stat.value or 0

        raise self.ToDataclassError(f"Bonus stat {stat_id} not found")

    def _get_stat_override_value(self, stat_id: StatId) -> int | None:
        for stat in self.override_stats:
            if stat.id == stat_id:
                return stat.value

        raise self.ToDataclassError(f"Override stat {stat_id} not found")

    def _get_stat_modifier_bonus_value(self, stat_id: StatId) -> int:
        STAT_ID_TO_BONUS_SUB_TYPE_ID = {
            StatId.STR: self.Modifiers.SubType.STR_SCORE,
            StatId.DEX: self.Modifiers.SubType.DEX_SCORE,
            StatId.CON: self.Modifiers.SubType.CON_SCORE,
            StatId.INT: self.Modifiers.SubType.INT_SCORE,
            StatId.WIS: self.Modifiers.SubType.WIS_SCORE,
            StatId.CHA: self.Modifiers.SubType.CHA_SCORE,
        }

        type_id = self.Modifiers.Type.BONUS
        sub_type_id = STAT_ID_TO_BONUS_SUB_TYPE_ID[stat_id]

        result = 0
        for modifier in self._get_filtered_modifiers(type_id, sub_type_id):
            if modifier.value is None:
                logger.warning("Bonus modifier has no value: %s", modifier)
                continue

            result += modifier.value

        return result

    def _get_ability_value(self, ability: models.CharacterAbility) -> int:
        CHARACTER_ABILITY_TO_STAT_ID = {
            models.CharacterAbility.STRENGTH: StatId.STR,
            models.CharacterAbility.DEXTERITY: StatId.DEX,
            models.CharacterAbility.CONSTITUTION: StatId.CON,
            models.CharacterAbility.INTELLIGENCE: StatId.INT,
            models.CharacterAbility.WISDOM: StatId.WIS,
            models.CharacterAbility.CHARISMA: StatId.CHA,
        }
        stat_id = CHARACTER_ABILITY_TO_STAT_ID[ability]

        override_value = self._get_stat_override_value(stat_id)
        if override_value is not None:
            return override_value

        return (
            self._get_stat_base_value(stat_id)
            + self._get_stat_bonus_value(stat_id)
            + self._get_stat_modifier_bonus_value(stat_id)
        )

    def _modifier_exists(self, type_: Modifiers.Type, sub_type: Modifiers.SubType) -> bool:
        for _ in self._get_filtered_modifiers(type_, sub_type):
            return True

        return False

    def _get_subtype_proficiency(self, sub_type: Modifiers.SubType) -> bool:
        return self._modifier_exists(self.Modifiers.Type.PROFICIENCY, sub_type)

    def _get_subtype_expertise(self, sub_type: Modifiers.SubType) -> bool:
        return self._modifier_exists(self.Modifiers.Type.EXPERTISE, sub_type)

    def _get_subtype_proficiency_bonus(self, sub_type: Modifiers.SubType) -> int:
        if self._get_subtype_expertise(sub_type):
            return 2 * self._get_proficiency_bonus()

        if self._get_subtype_proficiency(sub_type):
            return self._get_proficiency_bonus()

        return 0

    def _get_abilities(self) -> dict[models.CharacterAbility, int]:
        result: dict[models.CharacterAbility, int] = {}

        for ability in models.CharacterAbility:
            result[ability] = self._get_ability_value(ability)

        return result

    def _get_saving_throw_modifier_value(self, ability: models.CharacterAbility) -> int:
        ABILITY_TO_SAVING_THROW_SUB_TYPE_ID = {
            models.CharacterAbility.STRENGTH: self.Modifiers.SubType.STR_SAVING_THROW,
            models.CharacterAbility.DEXTERITY: self.Modifiers.SubType.DEX_SAVING_THROW,
            models.CharacterAbility.CONSTITUTION: self.Modifiers.SubType.CON_SAVING_THROW,
            models.CharacterAbility.INTELLIGENCE: self.Modifiers.SubType.INT_SAVING_THROW,
            models.CharacterAbility.WISDOM: self.Modifiers.SubType.WIS_SAVING_THROW,
            models.CharacterAbility.CHARISMA: self.Modifiers.SubType.CHA_SAVING_THROW,
        }
        sub_type_id = ABILITY_TO_SAVING_THROW_SUB_TYPE_ID[ability]

        return self._get_subtype_proficiency_bonus(sub_type_id)

    def _get_saving_throw_modifiers(self) -> dict[models.CharacterAbility, int]:
        result: dict[models.CharacterAbility, int] = {}

        for ability in models.CharacterAbility:
            result[ability] = self._get_saving_throw_modifier_value(ability)

        return result

    def _get_skill_modifier_value(self, skill: models.CharacterSkill) -> int:
        SKILL_TO_SUB_TYPE_ID = {
            models.CharacterSkill.ACROBATICS: self.Modifiers.SubType.ACROBATICS_SKILL,
            models.CharacterSkill.ANIMAL_HANDLING: self.Modifiers.SubType.ANIMAL_HANDLING_SKILL,
            models.CharacterSkill.ARCANA: self.Modifiers.SubType.ARCANA_SKILL,
            models.CharacterSkill.ATHLETICS: self.Modifiers.SubType.ATHLETICS_SKILL,
            models.CharacterSkill.DECEPTION: self.Modifiers.SubType.DECEPTION_SKILL,
            models.CharacterSkill.HISTORY: self.Modifiers.SubType.HISTORY_SKILL,
            models.CharacterSkill.INSIGHT: self.Modifiers.SubType.INSIGHT_SKILL,
            models.CharacterSkill.INTIMIDATION: self.Modifiers.SubType.INTIMIDATION_SKILL,
            models.CharacterSkill.INVESTIGATION: self.Modifiers.SubType.INVESTIGATION_SKILL,
            models.CharacterSkill.MEDICINE: self.Modifiers.SubType.MEDICINE_SKILL,
            models.CharacterSkill.NATURE: self.Modifiers.SubType.NATURE_SKILL,
            models.CharacterSkill.PERCEPTION: self.Modifiers.SubType.PERCEPTION_SKILL,
            models.CharacterSkill.PERFORMANCE: self.Modifiers.SubType.PERFORMANCE_SKILL,
            models.CharacterSkill.PERSUASION: self.Modifiers.SubType.PERSUASION_SKILL,
            models.CharacterSkill.RELIGION: self.Modifiers.SubType.RELIGION_SKILL,
            models.CharacterSkill.SLEIGHT_OF_HAND: self.Modifiers.SubType.SLEIGHT_OF_HAND_SKILL,
            models.CharacterSkill.STEALTH: self.Modifiers.SubType.STEALTH_SKILL,
            models.CharacterSkill.SURVIVAL: self.Modifiers.SubType.SURVIVAL_SKILL,
        }
        sub_type_id = SKILL_TO_SUB_TYPE_ID[skill]

        return self._get_subtype_proficiency_bonus(sub_type_id)

    def _get_skill_modifiers(self) -> dict[models.CharacterSkill, int]:
        result: dict[models.CharacterSkill, int] = {}

        for skill in models.CharacterSkill:
            result[skill] = self._get_skill_modifier_value(skill)

        return result

    def to_dataclass(self) -> models.Character:
        return models.Character(
            id=self.id,
            name=self.name,
            abilities=self._get_abilities(),
            saving_throw_modifiers=self._get_saving_throw_modifiers(),
            skill_modifiers=self._get_skill_modifiers(),
        )


@dataclasses.dataclass(frozen=True)
class CharacterDdbClient(protocols.CharacterRepositoryProtocol):
    base_client: aiohttp.ClientSession

    async def get(self, entity_id: int) -> models.Character:
        url = f"https://character-service.dndbeyond.com/character/v5/character/{entity_id}"

        async with self.base_client.get(url) as response:
            raw_response = await response.json()

        try:
            response = Response(**raw_response)
        except pydantic.ValidationError as e:
            logger.error("Failed to parse response: %s", raw_response)
            raise self.ResponseParseError from e

        if not response.success:
            logger.error("Failed to get character: message(%s) data(%s)", response.message, response.raw_data)

            try:
                error_data = ErrorData(**response.raw_data)
            except pydantic.ValidationError as e:
                logger.error("Failed to parse raw data: %s", response.raw_data)
                raise self.ResponseParseError from e

            if error_data.server_message == "The resource requested was not found.":
                raise self.NotFoundError

            if error_data.server_message == "Unauthorized Access Attempt.":
                raise self.AccessError

        try:
            data = CharacterData(**response.raw_data)
        except pydantic.ValidationError as e:
            logger.error("Failed to parse character: %s", response.raw_data)
            raise self.ResponseParseError from e

        try:
            return data.to_dataclass()
        except data.ToDataclassError as e:
            logger.error("Failed to convert to dataclass: %s", data)
            raise self.ResponseParseError from e


__all__ = [
    "CharacterDdbClient",
]
