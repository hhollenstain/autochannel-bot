"""Member join date context menu and slash command."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from autochannel.autochannel import AutoChannel

LOG = logging.getLogger(__name__)


async def _send_join_date(
    interaction: discord.Interaction, user: discord.Member | discord.User
) -> None:
    """Reply with when a member joined the guild.

    Args:
        interaction: The interaction to respond to.
        user: The member (or user, outside a guild) to look up.
    """
    LOG.debug(f"Show join date requested for {user}")
    joined_at = user.joined_at if isinstance(user, discord.Member) else None
    if joined_at is None:
        await interaction.response.send_message(f"Could not determine when {user} joined")
        return
    await interaction.response.send_message(f"{user} joined {discord.utils.format_dt(joined_at)}")


@app_commands.context_menu(name="Show Join Date")
async def show_join_date(interaction: discord.Interaction, member: discord.Member) -> None:
    """Context menu that shows when a member joined.

    discord.py does not allow context menus inside cogs, so this lives at
    module level and is added to the command tree in :func:`setup`.

    Args:
        interaction: The interaction that triggered the menu.
        member: The member that was right-clicked.
    """
    await _send_join_date(interaction, member)


class JoinCog(commands.Cog):
    """Cog for the ``/joined`` slash command."""

    def __init__(self, bot: AutoChannel) -> None:
        """Initialize the JoinCog.

        Args:
            bot: The bot instance.
        """
        self.bot = bot

    @app_commands.command(name="joined", description="Says when a member joined")
    @app_commands.describe(
        member="The member you want to get the joined date from; "
        "defaults to the user who uses the command"
    )
    async def joined(
        self, interaction: discord.Interaction, member: discord.Member | None = None
    ) -> None:
        """Show when a member joined.

        Args:
            interaction: The interaction that triggered the command.
            member: The member to show the join date for; defaults to the caller.
        """
        await _send_join_date(interaction, member or interaction.user)


async def setup(client: AutoChannel) -> None:
    """Register the join date cog and context menu.

    Args:
        client: The bot instance.
    """
    await client.add_cog(JoinCog(client))
    client.tree.add_command(show_join_date)


async def teardown(client: AutoChannel) -> None:
    """Remove the context menu when the extension is unloaded.

    Args:
        client: The bot instance.
    """
    client.tree.remove_command(show_join_date.name, type=show_join_date.type)
