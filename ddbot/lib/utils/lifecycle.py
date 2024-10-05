import dataclasses
import logging
import typing

AsyncCallback = typing.Awaitable[typing.Any]
SyncCallback = typing.Callable[[], typing.Any]
Callback = AsyncCallback | SyncCallback


@dataclasses.dataclass
class ShutdownCallback:
    callback: Callback
    error_message: str
    success_message: str

    @classmethod
    def from_disposable_resource(cls, name: str, dispose_callback: Callback) -> typing.Self:
        return cls(
            callback=dispose_callback,
            error_message=f"Failed to dispose {name}",
            success_message=f"{name} has been disposed",
        )


@dataclasses.dataclass
class StartupCallback:
    callback: Callback
    error_message: str
    success_message: str


@dataclasses.dataclass(frozen=True)
class LifecycleManager:
    logger: logging.Logger
    startup_callbacks: typing.Iterable[StartupCallback]
    shutdown_callbacks: typing.Iterable[ShutdownCallback]
    run_callback: AsyncCallback

    class StartupError(Exception): ...

    class ShutdownError(Exception): ...

    async def on_startup(self) -> None:
        for callback in self.startup_callbacks:
            try:
                if isinstance(callback.callback, typing.Awaitable):
                    await callback.callback
                else:
                    callback.callback()
            except Exception as error:
                self.logger.exception(callback.error_message)
                raise self.StartupError from error
            else:
                self.logger.info(callback.success_message)

    async def on_shutdown(self) -> None:
        errors: list[Exception] = []

        for callback in self.shutdown_callbacks:
            try:
                if isinstance(callback.callback, typing.Awaitable):
                    await callback.callback
                else:
                    callback.callback()
            except Exception as error:
                errors.append(error)
                self.logger.exception(callback.error_message)
            else:
                self.logger.info(callback.success_message)

        if len(errors) != 0:
            raise self.ShutdownError

    async def run(self) -> None:
        await self.run_callback


__all__ = [
    "LifecycleManager",
    "ShutdownCallback",
    "StartupCallback",
]
