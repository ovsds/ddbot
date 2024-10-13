import random
import typing

import pytest
import pytest_mock

import lib.character.models as character_models
import lib.character.services as character_services


@pytest.fixture(name="fixed_random_seed")
def fixture_fixed_random_seed() -> typing.Generator[None, None, None]:
    random.seed(42)
    try:
        yield
    finally:
        random.seed()


@pytest.mark.usefixtures("fixed_random_seed")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ability_value, expected_result",
    [
        (1, character_models.RollResult(value=4 - 5, details="4-5")),
        (10, character_models.RollResult(value=4 + 0, details="4+0")),
        (15, character_models.RollResult(value=4 + 2, details="4+2")),
        (20, character_models.RollResult(value=4 + 5, details="4+5")),
    ],
)
async def test_roll_ability_check(
    mocker: pytest_mock.MockFixture,
    ability_value: int,
    expected_result: character_models.RollResult,
):
    ability = character_models.CharacterAbility.STRENGTH
    service = character_services.RollService()
    character = mocker.Mock(spec=character_models.Character)
    character.abilities = {ability: ability_value}

    result = await service.roll_ability_check(character, ability)
    assert result == expected_result


@pytest.mark.usefixtures("fixed_random_seed")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ability_value, modifier_value, expected_result",
    [
        (1, -3, character_models.RollResult(value=4 - 5 - 3, details="4-8")),
        (10, 1, character_models.RollResult(value=4 + 0 + 1, details="4+1")),
        (15, 3, character_models.RollResult(value=4 + 2 + 3, details="4+5")),
        (20, 5, character_models.RollResult(value=4 + 5 + 5, details="4+10")),
    ],
)
async def test_roll_saving_throw(
    mocker: pytest_mock.MockFixture,
    ability_value: int,
    modifier_value: int,
    expected_result: character_models.RollResult,
):
    ability = character_models.CharacterAbility.STRENGTH
    service = character_services.RollService()
    character = mocker.Mock(spec=character_models.Character)
    character.abilities = {ability: ability_value}
    character.saving_throw_modifiers = {ability: modifier_value}

    result = await service.roll_saving_throw(character, ability)
    assert result == expected_result


@pytest.mark.usefixtures("fixed_random_seed")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ability_value, modifier_value, expected_result",
    [
        (1, -3, character_models.RollResult(value=4 - 5 - 3, details="4-8")),
        (10, 1, character_models.RollResult(value=4 + 0 + 1, details="4+1")),
        (15, 3, character_models.RollResult(value=4 + 2 + 3, details="4+5")),
        (20, 5, character_models.RollResult(value=4 + 5 + 5, details="4+10")),
    ],
)
async def test_roll_skill_check(
    mocker: pytest_mock.MockFixture,
    ability_value: int,
    modifier_value: int,
    expected_result: character_models.RollResult,
):
    ability = character_models.CharacterAbility.STRENGTH
    skill = character_models.CharacterSkill.ACROBATICS

    service = character_services.RollService()
    character = mocker.Mock(spec=character_models.Character)
    character.abilities = {ability: ability_value}
    character.skill_modifiers = {skill: modifier_value}

    result = await service.roll_skill_check(character, ability, skill)
    assert result == expected_result


@pytest.mark.usefixtures("fixed_random_seed")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ability_value, modifier_value, expected_result",
    [
        (1, -3, character_models.RollResult(value=4 - 5 - 3, details="4-8")),
        (10, 1, character_models.RollResult(value=4 + 0 + 1, details="4+1")),
        (15, 3, character_models.RollResult(value=4 + 2 + 3, details="4+5")),
        (20, 5, character_models.RollResult(value=4 + 5 + 5, details="4+10")),
    ],
)
async def test_roll_initiative(
    mocker: pytest_mock.MockFixture,
    ability_value: int,
    modifier_value: int,
    expected_result: character_models.RollResult,
):
    ability = character_models.CharacterAbility.DEXTERITY

    service = character_services.RollService()
    character = mocker.Mock(spec=character_models.Character)
    character.abilities = {ability: ability_value}
    character.initiative_modifier = modifier_value

    result = await service.roll_initiative(character)
    assert result == expected_result


@pytest.mark.usefixtures("fixed_random_seed")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "modifier_value, expected_result",
    [
        (-3, character_models.RollResult(value=4 - 3, details="4-3")),
        (1, character_models.RollResult(value=4 + 1, details="4+1")),
        (3, character_models.RollResult(value=4 + 3, details="4+3")),
        (5, character_models.RollResult(value=4 + 5, details="4+5")),
    ],
)
async def test_roll_death_saving_throw(
    mocker: pytest_mock.MockFixture,
    modifier_value: int,
    expected_result: character_models.RollResult,
):
    service = character_services.RollService()
    character = mocker.Mock(spec=character_models.Character)
    character.death_saving_throw_modifier = modifier_value

    result = await service.roll_death_saving_throw(character)
    assert result == expected_result
