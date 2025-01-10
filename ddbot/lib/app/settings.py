import typing
import warnings

import pydantic

import lib.telegram.command_handlers.help as help_command
import lib.utils.logging as logging_utils
import lib.utils.pydantic as pydantic_utils


class AppSettings(pydantic_utils.BaseSettingsModel):
    env: str = "production"
    debug: bool = False
    version: str = "unknown"

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_debug(self) -> bool:
        if not self.is_development and self.debug:
            warnings.warn("APP_DEBUG is True in non-development environment", UserWarning)

        return self.debug


class LoggingSettings(pydantic_utils.BaseSettingsModel):
    level: logging_utils.LogLevel = "INFO"
    format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


class ServerSettings(pydantic_utils.BaseSettingsModel):
    host: str = "localhost"
    port: int = 8080
    public_host: str = NotImplemented


class TelegramSettings(pydantic_utils.BaseSettingsModel):
    token: str = NotImplemented
    bot_name: str = "DndBeyond Character Bot"
    bot_short_description: str = "DndBeyond Character Bot"
    bot_description: str = "Telegram bot for rolling dices using DnD Beyond character sheets"
    help_message_template: str = help_command.DEFAULT_HELP_MESSAGE_TEMPLATE
    help_message_escape_characters: str = "_-."

    webhook_enabled: bool = True
    webhook_url: str = "/api/v1/telegram/webhook"
    webhook_secret_token: str = NotImplemented


class BaseContextRepositorySettings(pydantic_utils.BaseSettingsModel):
    type: typing.Any


class LocalContextRepositorySettings(BaseContextRepositorySettings):
    type: typing.Literal["local"] = "local"


class RedisContextRepositorySettings(BaseContextRepositorySettings):
    type: typing.Literal["redis"] = "redis"
    host: str = NotImplemented
    port: int = NotImplemented
    password: str = NotImplemented
    db: int = 0


CONTEXT_REPOSITORY_SETTINGS = {
    "local": LocalContextRepositorySettings,
    "redis": RedisContextRepositorySettings,
}


def _context_repository_settings_factory(data: typing.Any) -> BaseContextRepositorySettings:
    if isinstance(data, BaseContextRepositorySettings):
        return data

    assert isinstance(data, dict), "ContextRepositorySettings must be a dict"
    assert "type" in data, "ContextRepositorySettings must have a 'type' key"
    assert data["type"] in CONTEXT_REPOSITORY_SETTINGS, f"Unknown context repository type: {data['type']}"

    settings_class = CONTEXT_REPOSITORY_SETTINGS[data["type"]]

    return settings_class.model_validate(data)


class CharacterSettings(pydantic_utils.BaseSettingsModel):
    cache_ttl_seconds: int = 60 * 60


class Settings(pydantic_utils.BaseSettings):
    app: AppSettings = pydantic.Field(default_factory=AppSettings)
    logs: LoggingSettings = pydantic.Field(default_factory=LoggingSettings)
    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)
    telegram: TelegramSettings = pydantic.Field(default_factory=TelegramSettings)
    context: typing.Annotated[
        BaseContextRepositorySettings,
        pydantic.BeforeValidator(_context_repository_settings_factory),
    ] = pydantic.Field(default_factory=LocalContextRepositorySettings)
    character: CharacterSettings = pydantic.Field(default_factory=CharacterSettings)


__all__ = [
    "Settings",
]
