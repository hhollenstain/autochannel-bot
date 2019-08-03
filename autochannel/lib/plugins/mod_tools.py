import discord
import logging
from discord.ext import commands
from tamago.lib import utils

LOG = logging.getLogger(__name__)

class ModTools(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True, administrator=True)
    async def clear(self, ctx, amount=5):
        """
        Clears messages by !clear #ofmessages [@user]
        :param class self: tamago bot client
        :param context ctx: context of the message sent
        """
        channel = ctx.message.channel
        messages = []
        if ctx.message.mentions:
            mentions = []
            for member in ctx.message.mentions:
                mentions.append(member.id)
            async for message in channel.history(limit=int(amount) + 1):
                if message.author.id in mentions:
                    messages.append(message)
        else:
            async for message in channel.history(limit=int(amount) + 1):
                messages.append(message)

        await channel.delete_messages(messages)
        await ctx.send('{} messages purged'.format(len(messages)))

    @commands.command(name='getid', aliases=['id'], pass_context=True)
    @commands.has_permissions(manage_messages=True, administrator=True)
    async def getid(self, ctx):
        if not ctx.message.mentions:
            await ctx.send('{} is your UID'.format(ctx.message.author.id))
        else:
            embed = discord.Embed(
                title = 'UIDs of users',
                colour = discord.Colour.orange()
            )
            for member in ctx.message.mentions:
                embed.add_field(name=member.name, value=member.id, inline=False)

            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ModTools(client))
