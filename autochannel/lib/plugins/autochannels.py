import asyncio
import datetime
import datadog
import discord
import logging
import random
from datadog import ThreadStats
from discord import Game
from discord.ext import commands
from autochannel.lib import discordDog, utils

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
        # self.stats.increment('autochannel_bot.auto_channel_delete.count')

    @discordDog.dd_task_count
   # @self.autochannel.stats.agent.timed('autochannel_bot.task.ac_create_channel.time')
    #@discordDog.DDAgent.timed('autochannel_bot.task.ac_create_channel.time')
    async def ac_create_channel(self, cat, name=None):
        """
        """
        LOG.info(dir(discordDog.DDagent))
        self.stats.increment('autochannel_bot.auto_channel_create.count')
        created_channel = await cat.create_voice_channel(name)
        return created_channel

    @discordDog.dd_task_count
    async def vc_delete_channel(self, voicechannel, **kwargs):
        """
        insert logic to datadog metrics
        """
        reason = kwargs.get('reason')
        await voicechannel.delete(reason=reason)
        
    async def manage_auto_voice_channels(self, autochannel):
        """
        """
        for server in autochannel.guilds:
            categories = [cat for cat in server.categories if cat.name.lower() in autochannel.auto_categories]
            """ Gets a list of categories that are defined to watch """
            LOG.debug(f'Found these categories: {categories} matching in GUILD {server.name}')
            for cat in categories:
                auto_channels = [channel for channel in cat.voice_channels if  channel.name.startswith(autochannel.auto_channel_prefix)]
                empty_channel_list = [channel for channel in auto_channels if  len(channel.members) < 1]
                """ need a list of empty channels to decide wat to clean up """
                empty_channel_count = len(empty_channel_list)
                LOG.debug(f'GUILD: {server.name} category: {cat.name} empty channel count {empty_channel_count}')
                if empty_channel_count < 1:
                    channel_suffix = self.ac_channel_number(auto_channels)
                    LOG.debug(f' Channel created {autochannel.auto_channel_prefix} {cat.name.upper()}')
                    created_channel = await self.ac_create_channel(cat, name=f'{autochannel.auto_channel_prefix} {cat.name.upper()} - {channel_suffix}')
                    await created_channel.edit(position=1 + channel_suffix)
                if empty_channel_count > 1:
                    while len(empty_channel_list) > 1:
                        highest_empty_channel = self.ac_highest_empty_channel(empty_channel_list)
                        empty_channel_list.pop(empty_channel_list.index(highest_empty_channel))
                        await self.ac_delete_channel(highest_empty_channel)
                    LOG.info(f'TOO MANY CHANNELS in {cat.name}')

    def ac_highest_empty_channel(self, empty_auto_channels):
        """
        Takes in alist of empty channel objects and returns the channel object
        with the highest numbered suffix example channels '1', '5', '6' are in
        list but will return the '6' channel as the higest empty channel
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
        """
        valid_auto_channel
        """
        if (
                v_state is not None and
                v_state.channel is not None and
                v_state.channel.category is not None and
                v_state.channel.name.startswith(self.autochannel.auto_channel_prefix) and
                v_state.channel.category.name.lower() in self.autochannel.auto_categories
            ):
            return True
        else:
            return False

    # def valid_vc(self, cat):
    #     """
    #     checks if the vc checked is valid such as has a categorie and is in the
    #     auto_categories
    #     :param: object self: discord client
    #     :param: string cat: discord guild category 
    #     """
    #     if getattr(cat, 'name').lower() in self.autochannel.auto_categories:
    #         return True
    #     else:
    #         return False

    async def after_ac_task(self, after):
        """
        after_ac_task: handles the updates to the new channel the user entered
        :param: object self: discord client
        :param: object before: after state channel
        """
        cat = after.channel.category
        channel =  after.channel
        auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(self.autochannel.auto_channel_prefix)]
        empty_channel_count = len([channel for channel in auto_channels if  len(channel.members) < 1])
        if empty_channel_count < 1:
            channel_suffix = self.ac_channel_number(auto_channels)
            txt_channel_length = len(cat.text_channels)
            created_channel = await self.ac_create_channel(cat, f'{self.autochannel.auto_channel_prefix} {cat.name.upper()} - {channel_suffix}')
            LOG.debug(f'Updating channel: {created_channel.name} to position {channel_suffix + txt_channel_length} in category: {created_channel.category.name} ')
            await created_channel.edit(position=channel_suffix + txt_channel_length)

    async def before_ac_task(self, before):
        """
        before_ac_task: handles the updates to the old channel the user left
        :param: object self: discord client
        :param: object before: before state channel
        """
        cat = before.channel.category
        channel =  before.channel
        if len(before.channel.members) < 1:
            auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(self.autochannel.auto_channel_prefix) and len(channel.members) < 1]
            LOG.debug(f'empty autochannels for {cat.name}: {auto_channels}')
            empty_channel_count = len(auto_channels)
            if empty_channel_count > 1:
                highest_empty_channel = self.ac_highest_empty_channel(auto_channels)
                LOG.debug(f'last channel DC {before.channel.name}, but highest empty channel number is {highest_empty_channel.name}')
                await self.ac_delete_channel(highest_empty_channel, reason='AutoChannel does not like unused channels cluttering up his 720 display')

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
        LOG.debug(self.valid_auto_channel(before))

        if self.valid_auto_channel(before):
            await self.before_ac_task(before)

        if self.valid_auto_channel(after):
            await self.after_ac_task(after)

        if before.channel is not None and before.channel.name.startswith(self.autochannel.voice_channel_prefix):
            if len(before.channel.members) < 1:
                await before.channel.delete(reason='AutoChannel does not like unused channels cluttering up his 720 display')

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
