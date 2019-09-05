import asyncio
import datetime
import datadog
import discord
import logging
import random
from datadog import ThreadStats
from discord import Game
from discord.ext import commands
"""AC imports"""
from autochannel.lib import discordDog, utils
from autochannel.lib.discordDog import DDAgent
from autochannel.data.models import Guild, Category

LOG = logging.getLogger(__name__)

class ACMissingChannel(commands.CommandError):
    """Custom Exception class for unknown category errors."""

class ACUnknownCategory(commands.CommandError):
    """Custom Exception class for unknown category errors."""

class AutoChannels(commands.Cog):
    """
    """
    def __init__(self, autochannel):
        self.autochannel = autochannel
        self.stats = autochannel.stats

    @discordDog.dd_task_count
    async def ac_delete_channel(self, autochannel, **kwargs):
        """
        insert logic to datadog metrics
        """
        reason = kwargs.get('reason')
        await autochannel.delete(reason=reason)

    @discordDog.dd_task_count
    async def ac_create_channel(self, cat, name=None, **kwargs):
        """
        """
        created_channel = await cat.create_voice_channel(name, **kwargs)
        return created_channel

    @discordDog.dd_task_count
    async def vc_delete_channel(self, voicechannel, **kwargs):
        """
        insert logic to datadog metrics
        """
        reason = kwargs.get('reason')
        await voicechannel.delete(reason=reason)
        
    async def manage_auto_voice_channels(self, autochannel, guild=None):
        if guild:
            db_cats = list(self.autochannel.session.query(Category).with_entities(Category.id).filter_by(enabled=True, guild_id=guild.id).all())
            db_cats = [i[0] for i in db_cats]
            ac_guilds = []
            ac_guilds.append(guild)
        else:
            db_cats = list(self.autochannel.session.query(Category).with_entities(Category.id).filter_by(enabled=True).all())
            db_cats = [i[0] for i in db_cats]
            ac_guilds = autochannel.guilds
        
        for server in ac_guilds:
            categories = [cat for cat in server.categories if cat.id in db_cats]
            """checking if the db knows about the categorey"""
            for cat in categories:
                db_cat = self.autochannel.session.query(Category).get(cat.id)
                auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(db_cat.prefix)]
                empty_channel_list = [channel for channel in auto_channels if  len(channel.members) < 1]
                """ need a list of empty channels to decide wat to clean up """
                empty_channel_count = len(empty_channel_list)
                LOG.debug(f'GUILD: {server.name} category: {cat.name} empty channel count {empty_channel_count}')

                """
                Maybe split this into another function???
                """
                if empty_channel_count < 1:
                    channel_suffix = self.ac_channel_number(auto_channels)
                    LOG.debug(f' Channel created {db_cat.prefix} {cat.name.upper()}')
                    position = channel_suffix + len(cat.text_channels)
                    created_channel = await self.ac_create_channel(cat, name=f'{db_cat.prefix} {cat.name.upper()} - {channel_suffix}', guild=server.name, position=position)

                if empty_channel_count > 1:
                    while len(empty_channel_list) > 1:
                        highest_empty_channel = self.ac_highest_empty_channel(empty_channel_list)
                        empty_channel_list.pop(empty_channel_list.index(highest_empty_channel))
                        await self.ac_delete_channel(highest_empty_channel, guild=server.name)
                    LOG.info(f'TOO MANY CHANNELS in {cat.name}')

    def ac_highest_empty_channel(self, empty_auto_channels):
        """[summary]
        Takes in alist of empty channel objects and returns the channel object
        with the highest numbered suffix example channels '1', '5', '6' are in
        list but will return the '6' channel as the higest empty channel
        
        Arguments:
            empty_auto_channels {[list of channel objects]} -- list of empty
            channel objects
        """
        highest_empty_channel = None
        for ec in empty_auto_channels:
            if not highest_empty_channel:
                highest_empty_channel = ec
            if self.get_ac_channel(ec) > self.get_ac_channel(highest_empty_channel):
                        highest_empty_channel = ec
        return highest_empty_channel

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready by default will run when the bot is ready. This does some
        tasks incase the bot is down when users leave channels empty
        """
        await self.manage_auto_voice_channels(self.autochannel)

    @commands.command()
    @discordDog.dd_command_count
    async def acupdate(self, ctx):
        """
        
        Arguments:
            ctx {[type]} -- [description]
        """
        await self.manage_auto_voice_channels(self.autochannel, guild=ctx.guild)



    @commands.command(name='vc', aliases=['gc'])
    @discordDog.dd_command_count
    async def vc(self, ctx, *, gcrequest: str=''):
        """
        create voice channel vc <category> [optional suffix]
        """
        # self.stats.increment('autochannel_bot.command.vc.count')
        data =  await self.parse(ctx, gcrequest )
        if data['category'] is None:
            raise ACUnknownCategory(f'Unknown Discord category')
        if data['channel_suffix']:
            AC_suffix = data['channel_suffix']
        else:
            AC_suffix = self.vc_channel_number(ctx, data)


        cat_name = [cat for cat in ctx.guild.categories if cat.name.lower() in data['category']][0]
        created_channel = await ctx.guild.create_voice_channel(f'{self.autochannel.voice_channel_prefix} {data["category"]} {AC_suffix}', overwrites=None, category=cat_name, reason='AutoChannel bot automation')
        overwrite = discord.PermissionOverwrite()
        overwrite.manage_channels = True
        overwrite.manage_roles  = True
        await created_channel.set_permissions(ctx.message.author, overwrite=overwrite)
        invite_link = await self.ac_invite(ctx, created_channel)

        await ctx.send(f'AutoChannel made `{ctx.author}` a channel `{created_channel.name}`')
        await ctx.send(invite_link)
        await asyncio.sleep(60)
        if  len(created_channel.members) < 1:
            try:
                await self.vc_delete_channel(created_channel, reason='No one joined the custom channel after 60 seconds')
            except:
                raise ACMissingChannel(f'Channel already deleted')

    def valid_auto_channel(self, v_state):
        """[summary]
        
        Arguments:
            v_state {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        if(
                v_state is not None and
                v_state.channel is not None and
                v_state.channel.category is not None

          ):       
            category = self.autochannel.session.query(Category).get(v_state.channel.category.id)
            if (
                    category and 
                    category.enabled and 
                    v_state.channel.name.startswith(category.prefix)
                ):
                return True
            else:
                return False
        else:
            return False

    async def after_ac_task(self, after, member=None):
        """
        after_ac_task: handles the updates to the new channel the user entered
        :param: object self: discord client
        :param: object before: after state channel
        """
        cat = after.channel.category
        category = self.autochannel.session.query(Category).get(cat.id)
        auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(category.prefix)]
        empty_channel_count = len([channel for channel in auto_channels if  len(channel.members) < 1])
        if empty_channel_count < 1:
            channel_suffix = self.ac_channel_number(auto_channels)
            position =  channel_suffix + len(cat.text_channels)
            created_channel = await self.ac_create_channel(cat, name=f'{category.prefix} {cat.name.upper()} - {channel_suffix}', guild=member.guild, position=position)
            LOG.debug(f'Updating channel: {created_channel.name} to position {position} in category: {created_channel.category.name} ')

    async def before_ac_task(self, before, member=None):
        """
        before_ac_task: handles the updates to the old channel the user left
        :param: object self: discord client
        :param: object before: before state channel
        """
        cat = before.channel.category
        category = self.autochannel.session.query(Category).get(cat.id)
        if len(before.channel.members) < 1:
            auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(category.prefix) and len(channel.members) < 1]
            LOG.debug(f'empty autochannels for {cat.name}: {auto_channels}')
            empty_channel_count = len(auto_channels)
            if empty_channel_count > 1:
                highest_empty_channel = self.ac_highest_empty_channel(auto_channels)
                LOG.debug(f'last channel DC {before.channel.name}, but highest empty channel number is {highest_empty_channel.name}')
                await self.ac_delete_channel(highest_empty_channel, reason='AutoChannel does not like unused channels cluttering up his 720 display', guild=member.guild)

    @discordDog.dd_task_count
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Checks before and afer states of channels users leave and join
        this will handle logic to make sure there is no more than N (current
        defaulted to 1) empty channel at any time. This will also create a
        if less than N (current set to 1).
        :param: object self: discord client
        :param: object member: discord member
        :param: object before: before voice channel object 
        :param: object after: after voice channel object
        """
        if(
                    before.channel is not None and
                    before.channel.name.startswith(self.autochannel.voice_channel_prefix) and
                    len(before.channel.members) < 1
        ):  
            await self.vc_delete_channel(before.channel, reason="now empty")

        LOG.debug(self.valid_auto_channel(before))
        if self.valid_auto_channel(before):
            await self.before_ac_task(before, member=member)
        LOG.debug(self.valid_auto_channel(after))
        if self.valid_auto_channel(after):
            await self.after_ac_task(after, member=member)


        # category = self.autochannel.session.query(Category).get(before.channel.category.id)
        # if before.channel is not None and before.channel.name.startswith(category.prefix):
        #     if len(before.channel.members) < 1:
        #         await before.channel.delete(reason='AutoChannel does not like unused channels cluttering up his 720 display')

    def ac_channel_number(self, auto_channels):
        """
        returns number from auto prefix and returns the lowest number 
        :param: object self: discord client 
        :param: objects auto_channels: List of voice_channels objects 
        :returns the lowest number missing from the sequence of voice_channels
        """
        suffix_list = []
        for channel in auto_channels:
            suffix_list.append(int(''.join(channel.name.split(' ')[-1:])))

        return utils.missing_numbers(suffix_list)[0]

    def get_ac_channel(self, auto_channel):
        """
        returns the auto generated number suffix of a channel
        :param: obejct self: discord client
        :param: object auto_channel
        :returns the channel suffix number
        """
        return int(''.join(auto_channel.name.split(' ')[-1:]))

    def vc_channel_number(self, ctx, data):
        """
        returns the length of channel numbers 
        :param: object self: discord client 
        :param: object ctx: contex 
        :param: dictionary data: contains data information to utilize 
        """
        ac_channels = [vc for vc in ctx.guild.voice_channels if vc.name.startswith(f'{self.autochannel.voice_channel_prefix} {data["category"]}')]
        return (len(ac_channels) + 1)

    async def ac_invite(self, ctx, created_channel):
        """
        returns a invite link object for discord
        :param: object self: discord client
        :param: object CTX: context
        :param: object created_channel: discord channel 
        """
        invitelink = await created_channel.create_invite(reason='AutoChannel likes to make links')
        return invitelink

    async def parse(self, ctx, gcrequest):
        """
        returns data dictionary parsed from a context
        :param: object self: discord client
        :param: object ctx: context
        :param: string gcrequest: string from the command context
        returns  parsed data dictionary for consumptuion
        """
        server_cats = self.cat_names(ctx)
        category = None
        number_of_users = 10
        channel_suffix = []
        gcrequest = gcrequest.lower().split()
        data = {}
        for info in gcrequest:
            if info in server_cats:
                category = info
            else:
                channel_suffix.append(info)
        data['category'] = category
        data['channel_suffix'] = ' '.join(channel_suffix)
        data['number_of_users'] = number_of_users
        return data

    def cat_names(self, ctx):
        """
        used to et a list of category names
        :param: object self: discord client
        :param: object context: used mainly to find authors guild
        :returns list cat_list: list of categories from a discord guild
        """
        cat_list = []
        for cat in ctx.guild.categories:
            cat_list.append(cat.name.lower())
        return cat_list

    @vc.error 
    async def ac_handler(self, ctx, error):
        """
        """
        embed = discord.Embed(
            title = 'AutoChannel error',
            colour = discord.Colour.red()
        )
        if isinstance(error, ACUnknownCategory):
            msg = 'Unkonwn category, please type in an existing category in this Server'
        else:
            msg = error
        embed.add_field(name='Error', value=msg)
        await ctx.send(embed=embed)


def setup(autochannel):
    """
    """
    autochannel.add_cog(AutoChannels(autochannel))
