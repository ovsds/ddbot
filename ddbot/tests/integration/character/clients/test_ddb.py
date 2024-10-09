import typing

import aiohttp
import pytest
import pytest_asyncio

import lib.character.clients as ddb_clients
import lib.character.models as ddb_models


@pytest_asyncio.fixture(name="base_http_client")
async def fixture_base_http_client() -> typing.AsyncGenerator[aiohttp.ClientSession, None]:
    async with aiohttp.ClientSession() as client:
        yield client


@pytest.fixture(name="http_client")
def fixture_http_client(
    base_http_client: aiohttp.ClientSession,
) -> ddb_clients.CharacterDdbClient:
    return ddb_clients.CharacterDdbClient(base_http_client)


@pytest.fixture(name="character_id")
def fixture_character_id() -> int:
    return 133869351


@pytest.fixture(name="character_id_private")
def fixture_character_id_private() -> int:
    return 133870090


@pytest.fixture(name="character_id_not_found")
def fixture_character_id_not_found() -> int:
    return 987654321


@pytest.mark.asyncio
async def test_get_character(
    http_client: ddb_clients.CharacterDdbClient,
    character_id: int,
):
    expected = ddb_models.Character(
        id=character_id,
        name="Test_Character_Name",
        abilities={
            ddb_models.CharacterAbility.STRENGTH: 9,
            ddb_models.CharacterAbility.DEXTERITY: 2,
            ddb_models.CharacterAbility.CONSTITUTION: 4,
            ddb_models.CharacterAbility.INTELLIGENCE: 13,
            ddb_models.CharacterAbility.WISDOM: 10,
            ddb_models.CharacterAbility.CHARISMA: 17,
        },
        saving_throw_modifiers={
            ddb_models.CharacterAbility.STRENGTH: 0,
            ddb_models.CharacterAbility.DEXTERITY: 2,
            ddb_models.CharacterAbility.CONSTITUTION: 0,
            ddb_models.CharacterAbility.INTELLIGENCE: 2,
            ddb_models.CharacterAbility.WISDOM: 0,
            ddb_models.CharacterAbility.CHARISMA: 0,
        },
        skill_modifiers={
            ddb_models.CharacterSkill.ACROBATICS: 4,
            ddb_models.CharacterSkill.ANIMAL_HANDLING: 0,
            ddb_models.CharacterSkill.ARCANA: 0,
            ddb_models.CharacterSkill.ATHLETICS: 4,
            ddb_models.CharacterSkill.DECEPTION: 2,
            ddb_models.CharacterSkill.HISTORY: 0,
            ddb_models.CharacterSkill.INSIGHT: 2,
            ddb_models.CharacterSkill.INTIMIDATION: 0,
            ddb_models.CharacterSkill.INVESTIGATION: 0,
            ddb_models.CharacterSkill.MEDICINE: 0,
            ddb_models.CharacterSkill.NATURE: 0,
            ddb_models.CharacterSkill.PERCEPTION: 2,
            ddb_models.CharacterSkill.PERFORMANCE: 0,
            ddb_models.CharacterSkill.PERSUASION: 0,
            ddb_models.CharacterSkill.RELIGION: 0,
            ddb_models.CharacterSkill.SLEIGHT_OF_HAND: 2,
            ddb_models.CharacterSkill.STEALTH: 2,
            ddb_models.CharacterSkill.SURVIVAL: 2,
        },
    )

    character = await http_client.get(character_id)

    assert character == expected


@pytest.mark.asyncio
async def test_get_character_private(
    http_client: ddb_clients.CharacterDdbClient,
    character_id_private: int,
):
    with pytest.raises(ddb_clients.CharacterDdbClient.AccessError):
        await http_client.get(character_id_private)


@pytest.mark.asyncio
async def test_get_character_not_found(
    http_client: ddb_clients.CharacterDdbClient,
    character_id_not_found: int,
):
    with pytest.raises(ddb_clients.CharacterDdbClient.NotFoundError):
        await http_client.get(character_id_not_found)
