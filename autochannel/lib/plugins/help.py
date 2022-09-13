from typing import Optional
import discord
import logging
from discord import app_commands
from discord.ext import commands

LOG = logging.getLogger(__name__)

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command('help')

    @commands.command(pass_context=True)
    async def help(self, ctx):
        author = ctx.message.author

        embed = discord.Embed(
            colour = discord.Colour.blue(),
        )

        # embed.set_author(name='**Auto-chan**')
        embed.add_field(name='**Auto-chan**', value='Auto-chan auto creates/destroys voice channels in configured categories on http://auto-chan.io. Admins please configure the bot on the auto-chan.io dashboard')
        embed.add_field(name='**ADMIN ONLY**', value='''
                                                    **!acupdate**   => syncs with settings on http://auto-chan.io
                                                '''
                        )
        embed.add_field(name='**Commands**', value='''**!vc<category> <name of channel>** => used to create custom channel in enabled categories
                                                   ''', inline=False)

        await ctx.send(author, embed=embed)

    @self.client.tree.command()
    @app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
    async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Says when a member joined."""
        # If no member is explicitly provided then we use the command user here
        member = member or interaction.user

        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

async def setup(client):
    await client.add_cog(Help(client))


    # This context menu command only works on members
    @client.tree.context_menu(name='Show Join Date')
    async def show_join_date(interaction: discord.Interaction, member: discord.Member):
        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')