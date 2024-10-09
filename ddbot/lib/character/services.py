import dataclasses
import logging
import random

import lib.character.models as models
import lib.character.protocols as protocols
import lib.utils.cache as cache_utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class CharacterService(protocols.CharacterServiceProtocol):
    repository: protocols.CharacterRepositoryProtocol
    cache: cache_utils.CacheProtocol[models.Character]

    async def _get(self, entity_id: int) -> models.Character:
        try:
            return await self.repository.get(entity_id)
        except protocols.CharacterRepositoryProtocol.NotFoundError as e:
            raise protocols.CharacterServiceProtocol.NotFoundError from e
        except protocols.CharacterRepositoryProtocol.AccessError as e:
            raise protocols.CharacterServiceProtocol.AccessError from e
        except protocols.CharacterRepositoryProtocol.ResponseParseError as e:
            raise protocols.CharacterServiceProtocol.RepositoryError from e

    async def get(self, entity_id: int) -> models.Character:
        return await self.cache.wrap_awaitable(
            key=str(entity_id),
            awaitable=self._get(entity_id),
            logger=logger,
        )


class RollService:
    @staticmethod
    def _get_modifier_from_ability_score(ability_score: int) -> int:
        return (ability_score - 10) // 2

    @staticmethod
    def _get_roll_value() -> int:
        return random.randint(1, 20)

    async def roll_ability_check(
        self,
        character: models.Character,
        ability: models.CharacterAbility,
    ) -> models.RollResult:
        assert ability in character.abilities

        logger.debug(f"Rolling ability check for {ability} for {character}")

        ability_score = character.abilities[ability]

        modifier = self._get_modifier_from_ability_score(ability_score)
        roll_value = self._get_roll_value()

        return models.RollResult(value=roll_value + modifier, details=f"{roll_value}+{modifier}")

    def get_ability_check_callback(self, ability: models.CharacterAbility) -> protocols.RollCallbackProtocol:
        async def callback(character: models.Character) -> models.RollResult:
            return await self.roll_ability_check(character, ability)

        return callback

    async def roll_saving_throw(
        self,
        character: models.Character,
        ability: models.CharacterAbility,
    ) -> models.RollResult:
        assert ability in character.abilities
        assert ability in character.saving_throw_modifiers

        logger.debug(f"Rolling saving throw for {ability} for {character}")

        ability_score = character.abilities[ability]
        saving_throw_modifier = character.saving_throw_modifiers[ability]

        modifier = self._get_modifier_from_ability_score(ability_score) + saving_throw_modifier
        roll_value = self._get_roll_value()

        return models.RollResult(value=roll_value + modifier, details=f"{roll_value}+{modifier}")

    def get_saving_throw_callback(self, ability: models.CharacterAbility) -> protocols.RollCallbackProtocol:
        async def callback(character: models.Character) -> models.RollResult:
            return await self.roll_saving_throw(character, ability)

        return callback

    async def roll_skill_check(
        self,
        character: models.Character,
        ability: models.CharacterAbility,
        skill: models.CharacterSkill,
    ) -> models.RollResult:
        assert ability in character.abilities
        assert skill in character.skill_modifiers

        logger.debug(f"Rolling skill check for {skill} for {character}")

        ability_score = character.abilities[ability]
        skill_modifier = character.skill_modifiers[skill]

        modifier = self._get_modifier_from_ability_score(ability_score) + skill_modifier
        roll_value = self._get_roll_value()

        return models.RollResult(value=roll_value + modifier, details=f"{roll_value}+{modifier}")

    def get_skill_check_callback(
        self,
        ability: models.CharacterAbility,
        skill: models.CharacterSkill,
    ) -> protocols.RollCallbackProtocol:
        async def callback(character: models.Character) -> models.RollResult:
            return await self.roll_skill_check(character, ability, skill)

        return callback

    async def roll_initiative(
        self,
        character: models.Character,
    ) -> models.RollResult:
        assert models.CharacterAbility.DEXTERITY in character.abilities

        logger.debug(f"Rolling initiative for {character}")

        dexterity_score = character.abilities[models.CharacterAbility.DEXTERITY]

        modifier = self._get_modifier_from_ability_score(dexterity_score) + character.initiative_modifier
        roll_value = self._get_roll_value()

        return models.RollResult(value=roll_value + modifier, details=f"{roll_value}+{modifier}")


__all__ = [
    "CharacterService",
]
