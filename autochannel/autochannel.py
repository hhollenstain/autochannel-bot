"""Core AutoChannel Discord bot implementation with modern discord.py 2.x support."""

from __future__ import annotations

import logging
from typing import Any

import discord
from discord.ext import commands

from autochannel.data.database import DB

log = logging.getLogger("discord")


class AutoChannel(commands.Bot):
    """A custom Discord bot class with extended functionality for auto-channel management.

    This class extends discord.py's Bot class to provide automatic voice channel
    management, plugin system, and command handling.

    Attributes:
        app_id: Discord application ID.
        auto_channel_prefix: Prefix for auto-generated channels.
        auto_categories: List of category names to monitor.
        env: Environment identifier.
        voice_channel_prefix: Prefix for custom voice channels.
        initial_extensions: List of extension modules to load.
        testing_guild_id: Guild ID for testing commands.
    """

    def __init__(
        self,
        *args: Any,
        initial_extensions: list[str],
        **kwargs: Any,
    ) -> None:
        """Initialize the AutoChannel bot instance.

        Args:
            *args: Positional arguments for discord.ext.commands.Bot.
            initial_extensions: List of extension module names to load.
            **kwargs: Keyword arguments for discord.ext.commands.Bot.
        """
        super().__init__(*args, **kwargs)
        self._db = DB()
        self.app_id: str | None = kwargs.get("app_id")
        self.auto_channel_prefix: str = kwargs.get("auto_channel_prefix") or ""
        self.auto_categories: list[str] = kwargs.get("auto_categories", [])
        self.env: str = kwargs.get("env") or "dev"
        self.voice_channel_prefix: str = kwargs.get("voice_channel_prefix") or ""
        self.initial_extensions: list[str] = initial_extensions
        self.testing_guild_id: str | None = kwargs.get("testing_guild_id")

    async def setup_hook(self) -> None:
        """Setup hook called after bot is ready.

        Loads all extensions and syncs slash commands.
        If in testing mode, copies global commands to a test guild.
        """
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            g = discord.Object(int(self.testing_guild_id))
            self.tree.copy_global_to(guild=g)
            await self.tree.sync(guild=g)
            log.info(f"Commands successfully updated to GUILD: {g.id}")
        else:
            await self.tree.sync()

    async def close(self) -> None:
        """Close the database session when the bot is shutting down."""
        # Also close the database connection pool
        if hasattr(self, "_db") and self._db is not None:
            self._db.close_all_sessions()
        await super().close()
