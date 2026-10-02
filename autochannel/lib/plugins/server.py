from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from autochannel import VERSION
from autochannel.lib import utils

LOG = logging.getLogger(__name__)


class Server(commands.Cog):
    """Server information and status cog."""

    def __init__(self, autochannel: commands.Bot) -> None:
        """Initialize the Server cog.

        Args:
            autochannel: The bot instance.
        """
        self.autochannel = autochannel

    async def cog_load(self) -> None:
        """Initialize the cog and start background tasks."""
        LOG.info(f"Logged in as {self.autochannel.user.name}")
        await self.autochannel.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                name="Waking up, making coffee...", type=discord.ActivityType.playing
            ),
        )
        asyncio.create_task(utils.change_status(self.autochannel))
        asyncio.create_task(utils.list_servers(self.autochannel))
        asyncio.create_task(utils.list_users(self.autochannel))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle command errors.

        Args:
            ctx: The command context.
            error: The exception that occurred.
        """
        msg: str | None = None
        if isinstance(error, commands.CommandInvokeError):
            LOG.error(error)
            msg = f"{ctx.author.mention} Error running the command"
        elif isinstance(error, commands.CommandNotFound):
            msg = (
                f"{ctx.author.mention} the command you ran does not exist; "
                "please use !help for assistance"
            )
        elif isinstance(error, commands.CheckFailure):
            msg = (
                f":octagonal_sign: you do not have permission to "
                f"run this command; {ctx.author.mention}"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            msg = f"Missing required argument: ```{error}```"

        if msg is None:
            msg = f"Oh no, I have no idea what I am doing! {error}"

        await ctx.send(msg)

    @commands.command(name="autochannel", aliases=["autochan", "info"])
    async def autochannel(self, ctx: commands.Context) -> None:
        """Show information about the AutoChannel bot.

        Args:
            ctx: The command context.
        """
        embed = discord.Embed(
            description="AutoChannel Bot information",
            colour=discord.Color.green(),
        )

        avatar = "https://i.imgur.com/XFYjHsm.png"

        embed.set_author(name="AutoChannel Bot")
        embed.set_thumbnail(url=avatar)
        embed.add_field(
            name="description",
            value="Auto-chan manages voice channels creation, and custom voice channels. "
            "This is all managed via the auto-chan dashboard! "
            "[Add me](http://auto-chan.io)",
            inline=True,
        )
        # embed.add_field(
        #     name='Source Code',
        #     value=f'Want to see what makes me run? [Source Code Here!]'
        #     f'(https://github.com/hhollenstain/autochannel-bot)',
        #     inline=True,
        # )
        embed.add_field(
            name="**VOTE!**",
            value="If you enjoyed Auto-chan, please vote: https://top.gg/bot/606264038287998996",
        )
        embed.add_field(name="Version", value=VERSION, inline=True)

        await ctx.send(embed=embed)


async def setup(autochannel: commands.Bot) -> None:
    """Load the Server cog into the bot.

    Args:
        autochannel: The bot instance.
    """
    await autochannel.add_cog(Server(autochannel))
