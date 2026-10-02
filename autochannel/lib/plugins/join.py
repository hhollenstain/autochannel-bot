from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
from discord.member import Member

from autochannel.autochannel import AutoChannel

LOG = logging.getLogger(__name__)


async def setup(client: AutoChannel) -> None:
    """Setup the join date cog with context menu and slash commands.

    Args:
        client: The bot instance.
    """

    class JoinCog(commands.Cog):
        """Cog for join date commands and context menus."""

        def __init__(self, bot: AutoChannel) -> None:
            """Initialize the JoinCog.

            Args:
                bot: The bot instance.
            """
            self.bot = bot
            self.joined = app_commands.command(
                name="joined",
                description="Says when a member joined",
            )

        @app_commands.context_menu(name="Show Join Date")
        async def show_join_date_callback(
            self,
            interaction: Interaction[commands.Bot],
            member: Member,
        ) -> None:
            """Show when a member joined.

            Args:
                interaction: The interaction that triggered the command.
                member: The member to show the join date for.
            """
            LOG.debug(f"Show join date requested for {member}")
            await interaction.response.send_message(
                f"{member} joined at {discord.utils.format_dt(member.joined_at)}",
            )

        @app_commands.describe(
            member="The member you want to get the joined date from; "
            "defaults to the user who uses the command"
        )
        async def joined_callback(
            self,
            interaction: Interaction[commands.Bot],
            member: Member | None = None,
        ) -> None:
            """Show when a member joined.

            Args:
                interaction: The interaction that triggered the command.
                member: The member to show the join date for.
            """
            user = member or interaction.user
            LOG.debug(f"Show join date requested for {user}")
            await interaction.response.send_message(
                f"{user} joined {discord.utils.format_dt(user.joined_at)}",
            )

    join_cog = JoinCog(client)
    await client.add_cog(join_cog)
