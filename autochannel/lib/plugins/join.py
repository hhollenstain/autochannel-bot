from typing import Optional
import discord
from discord import app_commands, Interaction, Message, Member
from autochannel.autochannel import AutoChannel


async def setup(client: AutoChannel):
    # This context menu command only works on members
    @client.tree.context_menu(name='Show Join Date')
    async def show_join_date(interaction: Interaction, member: Member):
        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')



    @client.tree.command()
    @app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
    async def joined(interaction: Interaction, member: Optional[Member] = None):
        """Says when a member joined."""
        # If no member is explicitly provided then we use the command user here
        member = member or interaction.user

        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')
