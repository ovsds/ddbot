import asyncio
import dataclasses
import datetime
import logging
import typing

import aiogram
import aiogram.types as aiogram_types
import aiohttp
import redis.asyncio as redis_asyncio

import lib.app.errors as app_errors
import lib.app.settings as app_settings
import lib.character.clients as character_clients
import lib.character.models as character_models
import lib.character.services as character_services
import lib.context.repositories as context_repositories
import lib.context.services as context_services
import lib.telegram.command_handlers as telegram_command_handlers
import lib.telegram.lifecycle as telegram_lifecycle
import lib.utils.cache as cache_utils
import lib.utils.lifecycle as lifecycle_utils
import lib.utils.logging as logging_utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Application:
    lifecycle_manager: lifecycle_utils.LifecycleManager

    @classmethod
    def from_settings(cls, settings: app_settings.Settings) -> typing.Self:
        # Logging

        logging_utils.initialize(
            config=logging_utils.create_config(
                log_level=settings.logs.level,
                log_format=settings.logs.format,
                loggers={
                    "asyncio": logging_utils.LoggerConfig(
                        propagate=False,
                        level=settings.logs.level,
                    ),
                },
            ),
        )

        logger.info("Initializing application")

        startup_callbacks: list[lifecycle_utils.StartupCallback] = []
        shutdown_callbacks: list[lifecycle_utils.ShutdownCallback] = []

        # Clients

        logger.info("Initializing clients")

        aiohttp_client = aiohttp.ClientSession()
        shutdown_callbacks.append(
            lifecycle_utils.ShutdownCallback(
                callback=aiohttp_client.close(),
                error_message="Error while closing aiohttp client",
                success_message="Aiohttp client has been closed",
            ),
        )

        character_client = character_clients.CharacterDdbClient(
            base_client=aiohttp_client,
        )

        # Repositories

        logger.info("Initializing repositories")

        if isinstance(settings.context, app_settings.LocalContextRepositorySettings):
            logger.info("Using local context repository")
            context_repository = context_repositories.LocalContextRepository()
        elif isinstance(settings.context, app_settings.RedisContextRepositorySettings):
            logger.info("Using redis context repository")
            context_redis_client = redis_asyncio.Redis(
                host=settings.context.host,
                port=settings.context.port,
                db=settings.context.db,
                password=settings.context.password,
            )
            shutdown_callbacks.append(
                lifecycle_utils.ShutdownCallback(
                    callback=context_redis_client.aclose(),
                    error_message="Error while closing redis client",
                    success_message="Redis client has been closed",
                ),
            )
            context_repository = context_repositories.RedisContextRepository(
                redis_client=context_redis_client,
            )
        else:
            raise ValueError(f"Unknown context repository type: {settings.context.type}")

        character_cache = cache_utils.LocalCache[character_models.Character](
            ttl=datetime.timedelta(seconds=settings.character.cache_ttl_seconds),
        )

        # Services

        logger.info("Initializing services")

        context_service = context_services.LocalContextService(repository=context_repository)
        character_service = character_services.CharacterService(
            repository=character_client,
            cache=character_cache,
        )
        roll_service = character_services.RollService()

        # Telegram

        logger.info("Initializing telegram client")
        aiogram_bot = aiogram.Bot(token=settings.telegram.token)
        aiogram_dispatcher = aiogram.Dispatcher()
        aiogram_bot_commands: list[aiogram_types.BotCommand] = []

        # Handlers

        logger.info("Initializing command_handlers")

        help_command_handler = telegram_command_handlers.HelpCommandHandler(
            text=settings.telegram.help_message,
        )
        aiogram_dispatcher.message.register(help_command_handler.process, *help_command_handler.filters)
        aiogram_bot_commands.extend(help_command_handler.bot_commands)

        character_set_command_handler = telegram_command_handlers.CharacterSetCommandHandler(
            context_service=context_service,
            character_service=character_service,
        )
        aiogram_dispatcher.message.register(
            character_set_command_handler.process,
            *character_set_command_handler.filters,
        )
        aiogram_bot_commands.extend(character_set_command_handler.bot_commands)

        character_cache_clear_command_handler = telegram_command_handlers.CharacterCacheClear(
            context_service=context_service,
            cache=character_cache,
        )
        aiogram_dispatcher.message.register(
            character_cache_clear_command_handler.process,
            *character_cache_clear_command_handler.filters,
        )
        aiogram_bot_commands.extend(character_cache_clear_command_handler.bot_commands)

        for command in telegram_command_handlers.ABILITY_CHECK_COMMANDS:
            roll_command_handler = telegram_command_handlers.RollCommandHandler(
                context_service=context_service,
                character_service=character_service,
                roll_callback=roll_service.get_ability_check_callback(command.ability),
                command=command.command,
                description=command.description,
            )
            aiogram_dispatcher.message.register(
                roll_command_handler.process,
                *roll_command_handler.filters,
            )
            aiogram_bot_commands.extend(roll_command_handler.bot_commands)

        for command in telegram_command_handlers.SAVING_THROW_COMMANDS:
            roll_command_handler = telegram_command_handlers.RollCommandHandler(
                context_service=context_service,
                character_service=character_service,
                roll_callback=roll_service.get_saving_throw_callback(command.ability),
                command=command.command,
                description=command.description,
            )
            aiogram_dispatcher.message.register(
                roll_command_handler.process,
                *roll_command_handler.filters,
            )
            aiogram_bot_commands.extend(roll_command_handler.bot_commands)

        for command in telegram_command_handlers.SKILL_CHECK_COMMANDS:
            roll_command_handler = telegram_command_handlers.RollCommandHandler(
                context_service=context_service,
                character_service=character_service,
                roll_callback=roll_service.get_skill_check_callback(command.ability, command.skill),
                command=command.command,
                description=command.description,
            )
            aiogram_dispatcher.message.register(
                roll_command_handler.process,
                *roll_command_handler.filters,
            )
            aiogram_bot_commands.extend(roll_command_handler.bot_commands)

        logger.info("Initializing lifecycle manager")

        aiogram_lifecycle = telegram_lifecycle.AiogramLifecycle(
            aiogram_bot=aiogram_bot,
            bot_name=settings.telegram.bot_name,
            bot_short_description=settings.telegram.bot_short_description,
            bot_description=settings.telegram.bot_description,
            bot_commands=aiogram_bot_commands,
        )
        startup_callbacks.extend(aiogram_lifecycle.get_startup_callbacks())
        shutdown_callbacks.extend(aiogram_lifecycle.get_shutdown_callbacks())

        lifecycle_manager = lifecycle_utils.LifecycleManager(
            logger=logger,
            startup_callbacks=startup_callbacks,
            shutdown_callbacks=reversed(shutdown_callbacks),
            run_callback=aiogram_dispatcher.start_polling(aiogram_bot),
        )

        logger.info("Creating application")
        application = cls(
            lifecycle_manager=lifecycle_manager,
        )

        logger.info("Initializing application finished")

        return application

    async def start(self) -> None:
        try:
            await self.lifecycle_manager.on_startup()
        except lifecycle_utils.LifecycleManager.StartupError as start_error:
            logger.error("Application has failed to start")
            raise app_errors.ServerStartError("Application has failed to start, see logs above") from start_error

        logger.info("Application is starting")
        try:
            await self.lifecycle_manager.run()
        except asyncio.CancelledError:
            logger.info("Application has been interrupted")
        except BaseException as unexpected_error:
            logger.exception("Application runtime error")
            raise app_errors.ServerRuntimeError("Application runtime error") from unexpected_error

    async def dispose(self) -> None:
        logger.info("Application is shutting down...")

        try:
            await self.lifecycle_manager.on_shutdown()
        except lifecycle_utils.LifecycleManager.ShutdownError as dispose_error:
            logger.error("Application has shut down with errors")
            raise app_errors.DisposeError("Application has shut down with errors, see logs above") from dispose_error

        logger.info("Application has successfully shut down")


__all__ = [
    "Application",
]
