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
            description = 'Auto-chan auto creates/destroys voice channels in configured categories on http://auto-chan.io. Admins please configure the bot on the auto-chan.io dashboard'
        )

        embed.set_author(name='Auto-chan')
        embed.add_field(name='**!acupdate**', value='**ADMIN ONLY** syncs with settings on http://auto-chan.io', inline=False)
        embed.add_field(name='**!vc <category> <name of channel>**', value='used to create custom channel in enabled categories **EXAMPLE:** ```!vc mycategory mychannelname```', inline=False)

        await ctx.send(author, embed=embed)

def setup(client):
    client.add_cog(Help(client))
