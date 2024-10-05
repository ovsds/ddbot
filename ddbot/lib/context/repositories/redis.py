import dataclasses
import json
import logging

import redis.asyncio as redis_asyncio

import lib.context.models as models
import lib.context.protocols as protocols

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class RedisContextRepository(protocols.ContextRepositoryProtocol):
    redis_client: redis_asyncio.Redis

    @staticmethod
    def _get_full_key(key: str) -> str:
        return f"context:{key}"

    async def get(self, key: str) -> models.Context:
        full_key = self._get_full_key(key)
        raw_data = await self.redis_client.get(full_key)
        if raw_data is None:
            raise protocols.ContextRepositoryProtocol.NotFoundError

        # TODO: replace with proper library
        data = json.loads(raw_data)

        return models.Context(**data)

    async def set(self, key: str, context: models.Context):
        full_key = self._get_full_key(key)
        data = dataclasses.asdict(context)
        raw_data = json.dumps(data)

        await self.redis_client.set(full_key, raw_data)


__all__ = [
    "RedisContextRepository",
]
