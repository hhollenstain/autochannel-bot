from __future__ import annotations

import asyncio
import logging

import dbl
from discord.ext import commands

from autochannel.autochannel import AutoChannel

LOG = logging.getLogger(__name__)


class DiscordBotsOrgAPI(commands.Cog[AutoChannel]):
    """Handles interactions with the discordbots.org API"""

    def __init__(self, autochannel: AutoChannel) -> None:
        """Initialize the DBL cog.

        Args:
            autochannel: The AutoChannel bot instance.
        """
        self.autochannel = autochannel
        self.token: str | None = self.autochannel.dbl_token
        self.dblpy = dbl.DBLClient(self.autochannel, self.token)
        self.updating = self.autochannel.loop.create_task(self.update_stats())

    async def update_stats(self) -> None:
        """This function runs every 30 minutes to automatically update your server count"""
        while not self.autochannel.is_closed():
            if self.token:
                LOG.info("Attempting to post server count")
                try:
                    await self.dblpy.post_guild_count()
                    LOG.info(f"Posted server count ({self.dblpy.guild_count()})")
                except Exception as e:
                    LOG.exception(f"Failed to post server count\n{type(e).__name__}: {e}")
            else:
                LOG.info("Skipping DBL guild count, no API key")

            await asyncio.sleep(1800)


async def setup(autochannel: AutoChannel) -> None:
    """Load the DBL cog into the bot.

    Args:
        autochannel: The AutoChannel bot instance.
    """
    await autochannel.add_cog(DiscordBotsOrgAPI(autochannel))
