import discord
import logging
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

def setup(client):
    client.add_cog(Help(client))
