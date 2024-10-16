import typing

import lib.character.models as models


class CharacterRepositoryProtocol(typing.Protocol):
    class BaseError(Exception): ...

    class ResponseParseError(BaseError): ...

    class NotFoundError(BaseError): ...

    class AccessError(BaseError): ...

    async def get(self, entity_id: int) -> models.Character:
        """
        :raises NotFoundError
        :raises AccessError
        :raises ResponseParseError
        """
        ...


class CharacterServiceProtocol(typing.Protocol):
    class BaseError(Exception): ...

    class RepositoryError(BaseError): ...

    class NotFoundError(BaseError): ...

    class AccessError(BaseError): ...

    async def get(self, entity_id: int) -> models.Character:
        """
        :raises NotFoundError
        :raises AccessError
        :raises RepositoryError
        """
        ...


__all__ = [
    "CharacterRepositoryProtocol",
    "CharacterServiceProtocol",
]
