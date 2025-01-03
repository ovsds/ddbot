import asyncio
import dataclasses
import datetime
import logging
import typing

import aiogram
import aiogram.types as aiogram_types
import aiogram.webhook.aiohttp_server as aiogram_aiohttp_webhook
import aiohttp
import aiohttp.typedefs as aiohttp_typedefs
import aiohttp.web as aiohttp_web
import redis.asyncio as redis_asyncio

import lib.app.errors as app_errors
import lib.app.settings as app_settings
import lib.character.clients as character_clients
import lib.character.models as character_models
import lib.character.services as character_services
import lib.context.repositories as context_repositories
import lib.context.services as context_services
import lib.telegram.command_handlers as telegram_command_handlers
import lib.utils.aiogram as aiogram_utils
import lib.utils.aiohttp as aiohttp_utils
import lib.utils.cache as cache_utils
import lib.utils.lifecycle as lifecycle_utils
import lib.utils.logging as logging_utils

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Application:
    lifecycle: lifecycle_utils.Lifecycle

    @classmethod
    def from_settings(cls, settings: app_settings.Settings) -> typing.Self:
        log_level = "DEBUG" if settings.app.is_debug else settings.logs.level
        logging_config = logging_utils.create_config(
            log_level=log_level,
            log_format=settings.logs.format,
            loggers={
                "asyncio": logging_utils.LoggerConfig(
                    propagate=False,
                    level=log_level,
                ),
            },
        )
        logging_utils.initialize(config=logging_config)
        logger.info("Logging has been initialized with config: %s", logging_config)

        logger.info("Initializing application")

        lifecycle_main_tasks: list[asyncio.Task[typing.Any]] = []
        lifecycle_startup_callbacks: list[lifecycle_utils.Callback] = []
        lifecycle_shutdown_callbacks: list[lifecycle_utils.Callback] = []

        logger.info("Initializing global dependencies")

        aiohttp_client = aiohttp.ClientSession()
        lifecycle_shutdown_callbacks.append(
            lifecycle_utils.Callback(
                awaitable=aiohttp_client.close(),
                error_message="Error while closing aiohttp client",
                success_message="Aiohttp client has been closed",
            ),
        )

        logger.info("Initializing clients")

        character_client = character_clients.CharacterDdbClient(
            base_client=aiohttp_client,
        )

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
            lifecycle_shutdown_callbacks.append(
                lifecycle_utils.Callback(
                    awaitable=context_redis_client.aclose(),
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

        logger.info("Initializing services")

        context_service = context_services.LocalContextService(repository=context_repository)
        character_service = character_services.CharacterService(
            repository=character_client,
            cache=character_cache,
        )
        roll_service = character_services.RollService()

        logger.info("Initializing aiogram")

        aiogram_bot = aiogram.Bot(token=settings.telegram.token)
        aiogram_dispatcher = aiogram.Dispatcher()

        aiogram_general_commands: list[aiogram_types.BotCommand] = []
        aiogram_ability_check_commands: list[aiogram_types.BotCommand] = []
        aiogram_saving_throw_commands: list[aiogram_types.BotCommand] = []
        aiogram_skill_check_commands: list[aiogram_types.BotCommand] = []
        aiogram_miscellaneous_check_commands: list[aiogram_types.BotCommand] = []

        logger.info("Initializing aiogram handlers")

        character_set_command_handler = telegram_command_handlers.CharacterSetCommandHandler(
            context_service=context_service,
            character_service=character_service,
        )
        aiogram_dispatcher.message.register(
            character_set_command_handler.process,
            *character_set_command_handler.filters,
        )
        aiogram_general_commands.extend(character_set_command_handler.bot_commands)

        character_cache_clear_command_handler = telegram_command_handlers.CharacterCacheClear(
            context_service=context_service,
            cache=character_cache,
        )
        aiogram_dispatcher.message.register(
            character_cache_clear_command_handler.process,
            *character_cache_clear_command_handler.filters,
        )
        aiogram_general_commands.extend(character_cache_clear_command_handler.bot_commands)

        for command_factory in telegram_command_handlers.ABILITY_CHECK_COMMAND_FACTORIES:
            roll_command_handler = telegram_command_handlers.RollCommandHandler(
                context_service=context_service,
                character_service=character_service,
                command=command_factory.make(callback=roll_service.roll_ability_check),
            )
            aiogram_dispatcher.message.register(
                roll_command_handler.process,
                *roll_command_handler.filters,
            )
            aiogram_ability_check_commands.extend(roll_command_handler.bot_commands)

        for command_factory in telegram_command_handlers.ABILITY_SAVE_COMMAND_FACTORIES:
            roll_command_handler = telegram_command_handlers.RollCommandHandler(
                context_service=context_service,
                character_service=character_service,
                command=command_factory.make(callback=roll_service.roll_saving_throw),
            )
            aiogram_dispatcher.message.register(
                roll_command_handler.process,
                *roll_command_handler.filters,
            )
            aiogram_saving_throw_commands.extend(roll_command_handler.bot_commands)

        for command_factory in telegram_command_handlers.SKILL_CHECK_COMMAND_FACTORIES:
            roll_command_handler = telegram_command_handlers.RollCommandHandler(
                context_service=context_service,
                character_service=character_service,
                command=command_factory.make(callback=roll_service.roll_skill_check),
            )
            aiogram_dispatcher.message.register(
                roll_command_handler.process,
                *roll_command_handler.filters,
            )
            aiogram_skill_check_commands.extend(roll_command_handler.bot_commands)

        roll_command_handler = telegram_command_handlers.RollCommandHandler(
            context_service=context_service,
            character_service=character_service,
            command=telegram_command_handlers.INITIATIVE_COMMAND_FACTORY.make(roll_service.roll_initiative),
        )
        aiogram_dispatcher.message.register(
            roll_command_handler.process,
            *roll_command_handler.filters,
        )
        aiogram_miscellaneous_check_commands.extend(roll_command_handler.bot_commands)

        roll_command_handler = telegram_command_handlers.RollCommandHandler(
            context_service=context_service,
            character_service=character_service,
            command=telegram_command_handlers.DEATH_SAVE_COMMAND_FACTORY.make(roll_service.roll_death_saving_throw),
        )
        aiogram_dispatcher.message.register(
            roll_command_handler.process,
            *roll_command_handler.filters,
        )
        aiogram_miscellaneous_check_commands.extend(roll_command_handler.bot_commands)

        help_command_handler = telegram_command_handlers.HelpCommandHandler(
            text=telegram_command_handlers.render_help_message(
                template=settings.telegram.help_message_template,
                general_commands=aiogram_general_commands,
                ability_check_commands=aiogram_ability_check_commands,
                saving_throw_commands=aiogram_saving_throw_commands,
                skill_check_commands=aiogram_skill_check_commands,
                miscellaneous_check_commands=aiogram_miscellaneous_check_commands,
                escape_characters=settings.telegram.help_message_escape_characters,
            ),
        )
        aiogram_dispatcher.message.register(help_command_handler.process, *help_command_handler.filters)
        aiogram_general_commands.extend(help_command_handler.bot_commands)

        aiogram_lifecycle = aiogram_utils.Lifecycle(
            dispatcher=aiogram_dispatcher,
            bot=aiogram_bot,
            logger=logger,
            name=settings.telegram.bot_name,
            description=settings.telegram.bot_description,
            short_description=settings.telegram.bot_short_description,
            commands=[
                *aiogram_general_commands,
                *aiogram_ability_check_commands,
                *aiogram_saving_throw_commands,
                *aiogram_skill_check_commands,
                *aiogram_miscellaneous_check_commands,
            ],
            webhook=(
                aiogram_utils.Lifecycle.Webhook(
                    url=f"{settings.server.public_host}{settings.telegram.webhook_url}",
                    secret_token=settings.telegram.webhook_secret_token,
                )
                if settings.telegram.webhook_enabled
                else None
            ),
        )
        lifecycle_startup_callbacks.extend(aiogram_lifecycle.get_startup_callbacks())
        lifecycle_shutdown_callbacks.extend(aiogram_lifecycle.get_shutdown_callbacks())
        if not settings.telegram.webhook_enabled:
            lifecycle_main_tasks.append(aiogram_lifecycle.get_main_task())

        logger.info("Initializing aiohttp")

        aiohttp_url_dispatcher = aiohttp_web.UrlDispatcher()

        logger.info("Initializing aiohttp middlewares")

        aiohttp_middlewares: list[aiohttp_typedefs.Middleware] = []

        logger.info("Initializing aiohttp handlers")

        aiohttp_liveness_probe_handler = aiohttp_utils.LivenessProbeHandler()
        aiohttp_url_dispatcher.add_route("GET", "/api/v1/health/liveness", aiohttp_liveness_probe_handler.process)

        aiohttp_readiness_probe_handler = aiohttp_utils.ReadinessProbeHandler(
            subsystems=[],
        )
        aiohttp_url_dispatcher.add_route("GET", "/api/v1/health/readiness", aiohttp_readiness_probe_handler.process)

        if settings.telegram.webhook_enabled:
            aiohttp_telegram_webhook_handler = aiogram_aiohttp_webhook.SimpleRequestHandler(
                bot=aiogram_bot,
                dispatcher=aiogram_dispatcher,
                secret_token=settings.telegram.webhook_secret_token,
            )
            aiohttp_url_dispatcher.add_route(
                "POST",
                settings.telegram.webhook_url,
                aiohttp_telegram_webhook_handler.handle,
            )

        logger.info("Initializing aiohttp application")

        aiohttp_app = aiohttp_web.Application(
            middlewares=aiohttp_middlewares,
            router=aiohttp_url_dispatcher,
        )
        lifecycle_main_tasks.append(
            asyncio.create_task(
                coro=aiohttp_web._run_app(  # pyright: ignore[reportPrivateUsage]
                    app=aiohttp_app,
                    host=settings.server.host,
                    port=settings.server.port,
                    print=aiohttp_utils.PrintLogger(),
                ),
                name="aiohttp_app",
            )
        )

        logger.info("Initializing lifecycle manager")

        lifecycle = lifecycle_utils.Lifecycle(
            logger=logger,
            main_tasks=lifecycle_main_tasks,
            startup_callbacks=lifecycle_startup_callbacks,
            shutdown_callbacks=list(reversed(lifecycle_shutdown_callbacks)),
        )

        logger.info("Creating application")
        application = cls(
            lifecycle=lifecycle,
        )

        logger.info("Initializing application finished")

        return application

    async def start(self) -> None:
        try:
            await self.lifecycle.on_startup()
        except lifecycle_utils.Lifecycle.StartupError as start_error:
            logger.error("Application has failed to start")
            raise app_errors.ServerStartError("Application has failed to start, see logs above") from start_error

        logger.info("Application is starting")
        try:
            await self.lifecycle.run()
        except asyncio.CancelledError:
            logger.info("Application has been interrupted")
        except BaseException as unexpected_error:
            logger.exception("Application runtime error")
            raise app_errors.ServerRuntimeError("Application runtime error") from unexpected_error

    async def dispose(self) -> None:
        logger.info("Application is shutting down...")

        try:
            await self.lifecycle.on_shutdown()
        except lifecycle_utils.Lifecycle.ShutdownError as dispose_error:
            logger.error("Application has shut down with errors")
            raise app_errors.DisposeError("Application has shut down with errors, see logs above") from dispose_error

        logger.info("Application has successfully shut down")


__all__ = [
    "Application",
]
