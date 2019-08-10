import asyncio
import datetime
import discord
import logging
import random
import timeit
from discord import Game
from discord.ext import commands
from autochannel.lib import utils

LOG = logging.getLogger(__name__)

async def manage_auto_voice_channels(autochannel):
    """
    """
    purged_channel_count = 0
    for server in autochannel.guilds:
        categories = [cat for cat in server.categories if cat.name.lower() in autochannel.auto_categories]
        LOG.debug(f'Found these categories: {categories} matching in GUILD {server.name}')
        for cat in categories:
            empty_channel_count = 0
            auto_channels = [channel for channel in cat.voice_channels if  channel.name.startswith(autochannel.auto_channel_prefix)]
            for ac in auto_channels:
                if len(ac.members) < 1:
                   empty_channel_count += 1
            LOG.debug(f'GUILD: {server.name} category: {cat.name} empty channel count {empty_channel_count}')
            if empty_channel_count < 1:
                txt_channel_length = len(cat.text_channels)
                LOG.debug(f' Channel created {autochannel.auto_channel_prefix} {cat.name.upper()}')
                created_channel = await cat.create_voice_channel(f'{autochannel.auto_channel_prefix} {cat.name.upper()} - 1')
                await created_channel.edit(position=1 + txt_channel_length)

async def purge_unused_vc(autochannel):
    """
    """
    while not autochannel.is_closed():
        currentTime = datetime.datetime.utcnow()
        purged_channel_count = 0
        for server in autochannel.guilds:
            auto_channels = [vc for vc in server.voice_channels if  vc.name.startswith(autochannel.voice_channel_prefix)]
            for vc in auto_channels:
                if len(vc.members) < 1:
                    if utils.timediff(vc.created_at, currentTime) > 60:
                        purged_channel_count += 1
                        LOG.debug(f'Deleting Voice Channel: {vc.name} from GUILD: {server.name}')
                        await vc.delete(reason='AutoChannel does not like unused channels cluttering up his 720 display')
                    else:
                        LOG.debug(f'Voice Channel: {vc.name} in GUILD: {server.name} is only {utils.timediff(vc.created_at, currentTime)} seconds old')
        LOG.debug(f'Purged {purged_channel_count} Custom Channels this loop')
        await asyncio.sleep(60)

class ACMissingChannel(commands.CommandError):
    """Custom Exception class for unknown category errors."""

class ACUnknownCategory(commands.CommandError):
    """Custom Exception class for unknown category errors."""

class AutoChannels(commands.Cog):
    """
    """
    def __init__(self, autochannel):
        self.autochannel = autochannel

    @commands.Cog.listener()
    async def on_ready(self):
        """
        """
        await manage_auto_voice_channels(self.autochannel)

    @commands.command(name='vc', aliases=['gc'])
    async def vc(self, ctx, *, gcrequest: str=''):
        """
        create voice channel vc <category> [optional suffix]
        """
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
        await asyncio.sleep(10)
        if  len(created_channel.members) < 1:
            try:
                await created_channel.delete(reason='No one joined the custom channel after 60 seconds')
            except:
                raise ACMissingChannel(f'Channel already deleted')

    def valid_auto_channel(self, v_state):
        """
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

    def valid_vc(self, cat):
        """
        """
        if getattr(cat, 'name').lower() in self.autochannel.auto_categories:
            return True
        else:
            return False

    async def after_ac_task(self, after):
        """
        """
        cat = after.channel.category
        channel =  after.channel
        auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(self.autochannel.auto_channel_prefix)]
        empty_channel_count = 0
        for ac in auto_channels:
            if len(ac.members) < 1:
                empty_channel_count += 1
        if empty_channel_count < 1:
            channel_suffix = self.ac_channel_number(auto_channels)
            txt_channel_length = len(cat.text_channels)
            created_channel = await cat.create_voice_channel(f'{self.autochannel.auto_channel_prefix} {cat.name.upper()} - {channel_suffix}')
            LOG.debug(f'Updating channel: {created_channel.name} to position {channel_suffix + txt_channel_length} in category: {created_channel.category.name} ')
            await created_channel.edit(position=channel_suffix + txt_channel_length)

    async def before_ac_task(self, before):
        """
        """
        cat = before.channel.category
        channel =  before.channel
        if len(before.channel.members) < 1:
            auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(self.autochannel.auto_channel_prefix)]
            empty_channel_count = 0
            highest_empty_channel = None
            for ac in auto_channels:
                if len(ac.members) < 1:
                    LOG.debug(f'Channel name: {ac.name} has 0 members, Channel #: {self.get_ac_channel(ac)}' )
                    if self.get_ac_channel(ac) > self.get_ac_channel(before.channel):
                        highest_empty_channel = ac
                    empty_channel_count += 1
            if empty_channel_count > 1:
                if highest_empty_channel:
                    LOG.debug(f'last channel DC {before.channel.name}, but highest empty channel number is {highest_empty_channel.name}')
                    await highest_empty_channel.delete(reason='AutoChannel does not like unused channels cluttering up his 720 display')
                else:
                    await before.channel.delete(reason='AutoChannel does not like unused channels cluttering up his 720 display')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
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
        """
        return int(''.join(auto_channel.name.split(' ')[-1:]))

    def vc_channel_number(self, ctx, data):
        """
        """
        ac_channels = [vc for vc in ctx.guild.voice_channels if vc.name.startswith(f'{self.autochannel.voice_channel_prefix} {data["category"]}')]
        return (len(ac_channels) + 1)

    async def ac_invite(self, ctx, created_channel):
        """
        """
        invitelink = await created_channel.create_invite(reason='AutoChannel likes to make links')
        return invitelink

    async def parse(self, ctx, gcrequest):
        """
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
        """
        cat_list = []
        for cat in ctx.guild.categories:
            cat_list.append(cat.name.lower())
        return cat_list

    # @vc.error
    # async def ac_handler(self, ctx, error):
    #     """
    #     """
    #     embed = discord.Embed(
    #         title = 'AutoChannel error',
    #         colour = discord.Colour.red()
    #     )
    #     if isinstance(error, ACUnknownCategory):
    #         msg = 'Unkonwn category, please type in an existing category in this Server'
    #     else:
    #         msg = error
    #     embed.add_field(name='Error', value=msg)
    #     await ctx.send(embed=embed)


def setup(autochannel):
    """
    """
    autochannel.add_cog(AutoChannels(autochannel))
