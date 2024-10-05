import dataclasses
import logging

import lib.context.models as models
import lib.context.protocols as protocols

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class LocalContextRepository(protocols.ContextRepositoryProtocol):
    def __init__(self):
        self._contexts: dict[str, models.Context] = {}

    async def get(self, key: str) -> models.Context:
        if key not in self._contexts:
            raise protocols.ContextServiceProtocol.NotFoundError

        logger.debug(f"ContextServiceProtocol.get: {key}")
        return self._contexts[key]

    async def set(self, key: str, context: models.Context):
        logger.debug(f"ContextServiceProtocol.set: {key} {context}")
        self._contexts[key] = context


__all__ = [
    "LocalContextRepository",
]
