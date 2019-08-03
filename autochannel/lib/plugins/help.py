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
            colour = discord.Colour.orange()
        )

        embed.set_author(name='Help')
        embed.add_field(name='!ping', value='Returns Pong!', inline=False)
        embed.add_field(name='!8ball', value='Shakes Magic 8ball for answer', inline=False)

        await self.client.send_message(author, embed=embed)

def setup(client):
    client.add_cog(Help(client))
