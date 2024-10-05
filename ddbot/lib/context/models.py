import dataclasses


@dataclasses.dataclass(frozen=True)
class Context:
    character_id: int


__all__ = [
    "Context",
]
