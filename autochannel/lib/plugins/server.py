import discord
import logging
import random
from discord import Game
from discord.ext import commands
from autochannel import VERSION
from autochannel.lib import utils

LOG = logging.getLogger(__name__)



class Server(commands.Cog):
    def __init__(self, autochannel):
        self.autochannel = autochannel

    @commands.Cog.listener()
    async def on_ready(self):
        LOG.info('Logged in as {}'.format(self.autochannel.user.name))
        await self.autochannel.change_presence(status=discord.Status.online, activity=Game('Waking up, making coffee...'))
        self.autochannel.loop.create_task(utils.change_status(self.autochannel))
        self.autochannel.loop.create_task(utils.list_servers(self.autochannel))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            LOG.error(error)
            msg = '{} Error running the command'.format(ctx.message.author.mention)
        if isinstance(error, commands.CommandNotFound):
            msg = '{} the command you ran does not exist please use !help for assistance'.format(ctx.message.author.mention)
        if isinstance(error, commands.CheckFailure):
            msg = ':octagonal_sign: you do not have permission to run this command, {}'.format(ctx.message.author.mention)
        if isinstance(error, commands.MissingRequiredArgument):
            msg = 'Missing required argument: ```{}```'.format(error)

        if not msg:
            msg = 'Oh no, I have no idea what I am doing! {}'.format(error)


        await ctx.send('{}'.format(msg))

    @commands.command()
    async def autochannel(self, ctx):
        """
        Information about what makes Fakah run!
        """
        embed = discord.Embed(
            title = 'AutoChannel Bot',
            description = 'AutoChannel Bot information',
            colour = discord.Colour.green()
        )
        
        avatar = "https://i.imgur.com/XFYjHsm.png"

        embed.set_author(name='AutoChannel Bot')
        embed.set_thumbnail(url=avatar)
        embed.add_field(name='description', value=f'AutoChannel is a WIP, add AutoChannel bot to your server! [add me](http://auto-chan.io)', inline=True)
        # embed.add_field(name='Source Code', value=f'Want to see what makes me run? [Source Code Here!](https://github.com/hhollenstain/autochannel-bot)', inline=True)
        embed.add_field(name='Version', value=VERSION, inline=True)

        await ctx.send(embed=embed)

def setup(autochannel):
    autochannel.add_cog(Server(autochannel))
