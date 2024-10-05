import dataclasses

import aiogram

import lib.utils.lifecycle as lifecycle_manager_utils


@dataclasses.dataclass(frozen=True)
class AiogramLifecycle:
    aiogram_bot: aiogram.Bot
    bot_name: str
    bot_description: str
    bot_short_description: str
    bot_commands: list[aiogram.types.BotCommand]

    async def setup_telegram_bot_name(self) -> None:
        name = await self.aiogram_bot.get_my_name()

        if name.name != self.bot_name:
            await self.aiogram_bot.set_my_name(self.bot_name)

    async def setup_telegram_bot_description(self) -> None:
        description = await self.aiogram_bot.get_my_description()

        if description.description != self.bot_description:
            await self.aiogram_bot.set_my_description(self.bot_description)

    async def setup_telegram_bot_short_description(self) -> None:
        short_description = await self.aiogram_bot.get_my_short_description()

        if short_description.short_description != self.bot_short_description:
            await self.aiogram_bot.set_my_short_description(self.bot_short_description)

    async def setup_telegram_bot_commands(self) -> None:
        commands = await self.aiogram_bot.get_my_commands()
        expected_commands = self.bot_commands

        if commands != expected_commands:
            await self.aiogram_bot.set_my_commands(expected_commands)

    def get_startup_callbacks(self) -> list[lifecycle_manager_utils.StartupCallback]:
        return [
            lifecycle_manager_utils.StartupCallback(
                callback=self.setup_telegram_bot_name(),
                error_message="Failed to set telegram bot name",
                success_message="Telegram bot name has been set",
            ),
            lifecycle_manager_utils.StartupCallback(
                callback=self.setup_telegram_bot_description(),
                error_message="Failed to set telegram bot description",
                success_message="Telegram bot description has been set",
            ),
            lifecycle_manager_utils.StartupCallback(
                callback=self.setup_telegram_bot_short_description(),
                error_message="Failed to set telegram bot short description",
                success_message="Telegram bot short description has been set",
            ),
            lifecycle_manager_utils.StartupCallback(
                callback=self.setup_telegram_bot_commands(),
                error_message="Failed to set telegram bot commands",
                success_message="Telegram bot commands have been set",
            ),
        ]

    def get_shutdown_callbacks(self) -> list[lifecycle_manager_utils.ShutdownCallback]:
        return [
            lifecycle_manager_utils.ShutdownCallback(
                callback=self.aiogram_bot.session.close(),
                error_message="Failed to close telegram bot session",
                success_message="Telegram bot session has been closed",
            )
        ]


__all__ = [
    "AiogramLifecycle",
]
