import typing

import lib.context.models as context_models


class ContextRepositoryProtocol(typing.Protocol):
    class BaseError(Exception): ...

    class NotFoundError(BaseError): ...

    async def get(self, key: str) -> context_models.Context:
        """
        :raises NotFoundError
        """
        ...

    async def set(self, key: str, context: context_models.Context): ...


class ContextServiceProtocol(typing.Protocol):
    class BaseError(Exception): ...

    class NotFoundError(BaseError): ...

    async def get(self, key: str) -> context_models.Context:
        """
        :raises NotFoundError
        """
        ...

    async def set(self, key: str, context: context_models.Context): ...


__all__ = [
    "ContextRepositoryProtocol",
    "ContextServiceProtocol",
]
