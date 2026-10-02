"""Core AutoChannel Discord bot implementation with modern discord.py 2.x support."""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from autochannel.data.database import DB

log = logging.getLogger("discord")


class AutoChannel(commands.Bot):
    """A custom Discord bot class with extended functionality for auto-channel management.

    This class extends discord.py's Bot class to provide automatic voice channel
    management, plugin system, and command handling.

    Attributes:
        session: Database session for persisting configuration.
        app_id: Discord application ID.
        auto_channel_prefix: Prefix for auto-generated channels.
        auto_categories: List of category names to monitor.
        env: Environment identifier.
        dbl_token: DoubleBot token for stats.
        voice_channel_prefix: Prefix for custom voice channels.
        initial_extensions: List of extension modules to load.
        testing_guild_id: Guild ID for testing commands.
    """

    def __init__(
        self,
        *args: tuple,
        initial_extensions: list[str],
        **kwargs: dict,
    ) -> None:
        """Initialize the AutoChannel bot instance.

        Args:
            *args: Positional arguments for discord.ext.commands.Bot.
            initial_extensions: List of extension module names to load.
            **kwargs: Keyword arguments for discord.ext.commands.Bot.
        """
        super().__init__(*args, **kwargs)
        db = DB()
        self.session = db.session()
        self.app_id: str | None = kwargs.get("app_id")
        self.auto_channel_prefix: str = kwargs.get("auto_channel_prefix")
        self.auto_categories: list[str] = kwargs.get("auto_categories", [])
        self.env: str = kwargs.get("env") or "dev"
        self.dbl_token: str | None = kwargs.get("dbl_token")
        self.stats: None = None
        self.voice_channel_prefix: str = kwargs.get("voice_channel_prefix")
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
