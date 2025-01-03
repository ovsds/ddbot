import os
import typing
import warnings

import pydantic
import pydantic_settings

import lib.telegram.command_handlers.help as help_command
import lib.utils.logging as logging_utils


class AppSettings(pydantic.BaseModel):
    env: str = "production"
    debug: bool = False

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_debug(self) -> bool:
        if not self.is_development and self.debug:
            warnings.warn("APP_DEBUG is True in non-development environment", UserWarning)

        return self.debug


class LoggingSettings(pydantic.BaseModel):
    level: logging_utils.LogLevel = "INFO"
    format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


class ServerSettings(pydantic.BaseModel):
    host: str = "localhost"
    port: int = 8080
    public_host: str = NotImplemented


class TelegramSettings(pydantic_settings.BaseSettings):
    token: str = NotImplemented
    bot_name: str = "DndBeyond Character Bot"
    bot_short_description: str = "DndBeyond Character Bot"
    bot_description: str = "Telegram bot for rolling dices using DnD Beyond character sheets"
    help_message_template: str = help_command.DEFAULT_HELP_MESSAGE_TEMPLATE
    help_message_escape_characters: str = "_-."

    webhook_enabled: bool = True
    webhook_url: str = "/api/v1/telegram/webhook"
    webhook_secret_token: str = NotImplemented


class BaseContextRepositorySettings(pydantic_settings.BaseSettings):
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


class CharacterSettings(pydantic_settings.BaseSettings):
    cache_ttl_seconds: int = 60 * 60


class Settings(pydantic_settings.BaseSettings):
    app: AppSettings = pydantic.Field(default_factory=AppSettings)
    logs: LoggingSettings = pydantic.Field(default_factory=LoggingSettings)
    server: ServerSettings = pydantic.Field(default_factory=ServerSettings)
    telegram: TelegramSettings = pydantic.Field(default_factory=TelegramSettings)
    context: typing.Annotated[
        BaseContextRepositorySettings,
        pydantic.BeforeValidator(_context_repository_settings_factory),
    ] = pydantic.Field(default_factory=LocalContextRepositorySettings)
    character: CharacterSettings = pydantic.Field(default_factory=CharacterSettings)

    model_config = pydantic_settings.SettingsConfigDict(
        env_nested_delimiter="__",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        init_settings: pydantic_settings.PydanticBaseSettingsSource,
        env_settings: pydantic_settings.PydanticBaseSettingsSource,
        dotenv_settings: pydantic_settings.PydanticBaseSettingsSource,
        file_secret_settings: pydantic_settings.PydanticBaseSettingsSource,
    ) -> tuple[pydantic_settings.PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            pydantic_settings.YamlConfigSettingsSource(
                settings_cls,
            ),
            *cls.settings_yaml_sources(settings_cls),
        )

    @classmethod
    def settings_yaml_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
    ) -> typing.Sequence[pydantic_settings.YamlConfigSettingsSource]:
        yaml_file_path = os.environ.get("SETTINGS_YAML", None)

        if yaml_file_path is None:
            return []

        if not os.path.exists(yaml_file_path):
            raise FileNotFoundError(f"Settings file not found: {yaml_file_path}")

        return [
            pydantic_settings.YamlConfigSettingsSource(
                settings_cls,
                yaml_file=yaml_file_path,
            )
        ]


__all__ = [
    "Settings",
]
