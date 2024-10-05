import dataclasses
import datetime
import logging
import typing

T = typing.TypeVar("T")


class CacheProtocol(typing.Protocol[T]):
    async def wrap_awaitable(self, key: str, awaitable: typing.Awaitable[T], logger: logging.Logger) -> T: ...

    async def clear(self, key: str) -> None: ...


@dataclasses.dataclass
class NoCache(CacheProtocol[T]):
    async def wrap_awaitable(self, key: str, awaitable: typing.Awaitable[T], logger: logging.Logger) -> T:
        logger.debug("NoCache.wrap_awaitable: key=%s", key)
        return await awaitable

    async def clear(self, key: str) -> None:
        pass


@dataclasses.dataclass
class _LocalCacheRecord(typing.Generic[T]):
    value: T
    created_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)
    ttl: datetime.timedelta = datetime.timedelta()

    def is_expired(self) -> bool:
        return self.age > self.ttl

    @property
    def age(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.created_at


@dataclasses.dataclass
class LocalCache(CacheProtocol[T]):
    ttl: datetime.timedelta

    _cache: dict[str, _LocalCacheRecord[T]] = dataclasses.field(default_factory=dict)

    async def _update_record(self, key: str, awaitable: typing.Awaitable[T]) -> T:
        value = await awaitable
        self._cache[key] = _LocalCacheRecord(value=value, ttl=self.ttl)
        return value

    async def wrap_awaitable(self, key: str, awaitable: typing.Awaitable[T], logger: logging.Logger) -> T:
        if key not in self._cache:
            logger.debug("LocalCache.wrap_awaitable: key=%s, cache miss", key)
            return await self._update_record(key, awaitable)

        record = self._cache[key]

        if record.is_expired():
            logger.debug("LocalCache.wrap_awaitable: key=%s, cache expired", key)
            return await self._update_record(key, awaitable)

        logger.debug(
            "LocalCache.wrap_awaitable: key=%s, cache hit, record age: %s, ttl: %s", key, record.age, record.ttl
        )
        return record.value

    async def clear(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]


__all__ = [
    "CacheProtocol",
    "LocalCache",
    "NoCache",
]
