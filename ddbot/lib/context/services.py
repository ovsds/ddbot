import dataclasses
import logging

import lib.context.models as models
import lib.context.protocols as protocols

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class LocalContextService(protocols.ContextServiceProtocol):
    repository: protocols.ContextRepositoryProtocol

    async def get(self, key: str) -> models.Context:
        try:
            return await self.repository.get(key)
        except protocols.ContextRepositoryProtocol.NotFoundError:
            raise protocols.ContextServiceProtocol.NotFoundError

    async def set(self, key: str, context: models.Context):
        await self.repository.set(key, context)


__all__ = [
    "LocalContextService",
]
