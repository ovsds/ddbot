import dataclasses
import enum
import typing


class CharacterAbility(enum.Enum):
    STRENGTH = enum.auto()
    DEXTERITY = enum.auto()
    CONSTITUTION = enum.auto()
    INTELLIGENCE = enum.auto()
    WISDOM = enum.auto()
    CHARISMA = enum.auto()


class CharacterSkill(enum.Enum):
    ACROBATICS = enum.auto()
    ANIMAL_HANDLING = enum.auto()
    ARCANA = enum.auto()
    ATHLETICS = enum.auto()
    DECEPTION = enum.auto()
    HISTORY = enum.auto()
    INSIGHT = enum.auto()
    INTIMIDATION = enum.auto()
    INVESTIGATION = enum.auto()
    MEDICINE = enum.auto()
    NATURE = enum.auto()
    PERCEPTION = enum.auto()
    PERFORMANCE = enum.auto()
    PERSUASION = enum.auto()
    RELIGION = enum.auto()
    SLEIGHT_OF_HAND = enum.auto()
    STEALTH = enum.auto()
    SURVIVAL = enum.auto()


@dataclasses.dataclass
class Character:
    id: int
    name: str
    abilities: typing.Mapping[CharacterAbility, int]
    saving_throw_modifiers: typing.Mapping[CharacterAbility, int]
    skill_modifiers: typing.Mapping[CharacterSkill, int]
    initiative_modifier: int
    death_saving_throw_modifier: int


@dataclasses.dataclass
class RollResult:
    value: int
    details: str


__all__ = [
    "Character",
    "CharacterAbility",
    "CharacterSkill",
    "RollResult",
]
