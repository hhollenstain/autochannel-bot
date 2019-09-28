import asyncio
import datetime
import discord
import logging
import random
import re
import time
from discord import Game
from discord.ext import commands
from profanityfilter import ProfanityFilter
"""AC imports"""
from autochannel.lib import utils
from autochannel.lib.metrics import command_metrics_counter, task_metrics_counter, COMMAND_SUMMARY_VC, COMMAND_SUMMARY_ACUPDATE
from autochannel.data.models import Guild, Category

LOG = logging.getLogger(__name__)

pf = ProfanityFilter(no_word_boundaries = True)

class ACMissingChannel(commands.CommandError):
    """Custom Exception class for unknown category errors."""

class ACUnknownCategory(commands.CommandError):
    """Custom Exception class for unknown category errors."""

class ACDisabledCustomCategory(commands.CommandInvokeError):
    """Custom Exception class for disabled custom voice category"""

class VCProfaneWordused(commands.CommandInvokeError):
    """custom Exception class for profane word use""" 

class AutoChannels(commands.Cog):
    """
    """
    def __init__(self, autochannel):
        self.autochannel = autochannel
        self.stats = autochannel.stats

    @task_metrics_counter
    async def ac_delete_channel(self, autochannel, **kwargs):
        """
        insert logic to datadog metrics
        """
        reason = kwargs.get('reason')
        await autochannel.delete(reason=reason)

    @task_metrics_counter
    async def ac_create_channel(self, cat, name=None, **kwargs):
        """
        """
        created_channel = await cat.create_voice_channel(name, **kwargs)
        return created_channel

    @task_metrics_counter
    async def vc_delete_channel(self, voicechannel, **kwargs):
        """
        insert logic to datadog metrics 
        """
        reason = kwargs.get('reason')
        await voicechannel.delete(reason=reason)
        
    async def manage_auto_voice_channels(self, autochannel, guild=None):
        db_cats_disabled = None
        if guild:
            db_cats = list(self.autochannel.session.query(Category).with_entities(Category.id).filter_by(enabled=True, guild_id=guild.id).all())
            db_cats = [i[0] for i in db_cats]
            db_cats_disabled = list(self.autochannel.session.query(Category).with_entities(Category.id).filter_by(enabled=False, guild_id=guild.id).all())
            db_cats_disabled = [i[0] for i in db_cats_disabled]
            ac_guilds = []
            ac_guilds.append(guild)
        else:
            db_cats = list(self.autochannel.session.query(Category).with_entities(Category.id).filter_by(enabled=True).all())
            db_cats = [i[0] for i in db_cats]
            ac_guilds = autochannel.guilds
        
        for server in ac_guilds:
            if db_cats_disabled:
                """ Runs if we have are calling the acupdate"""
                categories = [cat for cat in server.categories if cat.id in db_cats_disabled]
                for cat in categories:
                    db_cat = self.autochannel.session.query(Category).get(cat.id)
                    auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(db_cat.prefix)]
                    for channel in auto_channels:
                        await self.ac_delete_channel(channel, guild=server.name)
            
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
                if empty_channel_count < db_cat.empty_count:
                    while empty_channel_count < db_cat.empty_count:
                        channel_suffix = self.ac_channel_number(auto_channels)
                        LOG.debug(f' Channel created {db_cat.prefix}')
                        position = channel_suffix + len(cat.text_channels)
                        await self.ac_create_channel(cat, name=f'{db_cat.prefix} - {channel_suffix}', guild=server.name, position=position, user_limit=db_cat.channel_size)
                        empty_channel_count += 1
                        auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(db_cat.prefix)]

                if empty_channel_count > 1:
                    while len(empty_channel_list) > db_cat.empty_count:
                        highest_empty_channel = self.ac_highest_empty_channel(empty_channel_list)
                        empty_channel_list.pop(empty_channel_list.index(highest_empty_channel))
                        LOG.debug(f'Deleting too many empty channels form {server.name}: {highest_empty_channel}')
                        await self.ac_delete_channel(highest_empty_channel, guild=server.name)

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
    @commands.has_permissions(administrator=True)
    @command_metrics_counter
    @COMMAND_SUMMARY_ACUPDATE.time()
    async def acupdate(self, ctx):
        """
        
        Arguments:
            ctx {[type]} -- [description]
        """
        embed = discord.Embed(
            title = 'AutoChannel update',
            colour = discord.Colour.green()
        )
        msg = 'Syncd AutoChannel settings with server'
        embed.add_field(name='Success', value=msg)
        await self.manage_auto_voice_channels(self.autochannel, guild=ctx.guild)
        await ctx.send(embed=embed)

    @commands.command(name='vc', aliases=['gc'])
    @command_metrics_counter
    async def vc(self, ctx, *, gcrequest: str=''):
        """
        create voice channel vc <category> [optional suffix]
        """
        # self.stats.increment('autochannel_bot.command.vc.count')
        data =  await self.parse(ctx, gcrequest )
        if data['category'] is None:
            raise ACUnknownCategory(f'Unknown Discord category')

        cat_name = [cat for cat in ctx.guild.categories if cat.name.lower() in data['category'].lower()][0]
        category = self.autochannel.session.query(Category).get(cat_name.id)

        if data['channel_suffix']:
            AC_suffix = data['channel_suffix']
            if pf.is_profane(AC_suffix):
                raise VCProfaneWordused(f'Used a profane word when creating a custom voice channel')
        else:
            AC_suffix = self.vc_channel_number(ctx, data, category)

        if not category or not category.custom_enabled:
            raise ACDisabledCustomCategory(f'Category {cat_name.name} is disabled. To use custom channels in this category an **ADMIN** must enable:  http://auto-chan.io')
        
        created_channel = await ctx.guild.create_voice_channel(f'{category.custom_prefix} {AC_suffix}', overwrites=None, category=cat_name, reason='AutoChannel bot automation')
        # overwrite = discord.PermissionOverwrite()
        # overwrite.manage_channels = True
        # overwrite.manage_roles  = True
        # await created_channel.set_permissions(ctx.message.author, overwrite=overwrite)
        invite_link = await self.ac_invite(ctx, created_channel)

        await ctx.send(f'AutoChannel made `{ctx.author}` a channel `{created_channel.name}`')
        await ctx.send(invite_link)
        await asyncio.sleep(60)
        if  len(created_channel.members) < 1:
            try:
                await self.vc_delete_channel(created_channel, reason='No one joined the custom channel after 60 seconds')
            except:
                """annoying to see this error doesn't add value to the end user"""
                pass

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
        if empty_channel_count < category.empty_count:
            channel_suffix = self.ac_channel_number(auto_channels)
            position =  channel_suffix + len(cat.text_channels)
            created_channel = await self.ac_create_channel(cat, name=f'{category.prefix} - {channel_suffix}', guild=member.guild, position=position, user_limit=category.channel_size)
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
            if empty_channel_count > category.empty_count:
                highest_empty_channel = self.ac_highest_empty_channel(auto_channels)
                LOG.debug(f'last channel DC {before.channel.name}, but highest empty channel number is {highest_empty_channel.name}')
                await self.ac_delete_channel(highest_empty_channel, reason='AutoChannel does not like unused channels cluttering up his 720 display', guild=member.guild)

    @task_metrics_counter
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
                    before.channel.category is not None and
                    len(before.channel.members) < 1
        ):  
            category = self.autochannel.session.query(Category).get(before.channel.category_id)
            if category and before.channel.name.startswith(f'{category.custom_prefix}'):
                await self.vc_delete_channel(before.channel, reason="now empty")

        LOG.debug(self.valid_auto_channel(before))
        if self.valid_auto_channel(before):
            await self.before_ac_task(before, member=member)
        LOG.debug(self.valid_auto_channel(after))
        if self.valid_auto_channel(after):
            await self.after_ac_task(after, member=member)

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

    def vc_channel_number(self, ctx, data, category):
        """
        returns the length of channel numbers 
        :param: object self: discord client 
        :param: object ctx: contex 
        :param: dictionary data: contains data information to utilize 
        """
        ac_channels = [vc for vc in ctx.guild.voice_channels if str(vc.category).lower().startswith(f'{data["category"]}') and vc.name.startswith(category.custom_prefix)]
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
        channel_suffix = None
        gcrequest_list = gcrequest.split()
        data = {}
        """ Checking to see if category is in the string of data everything else is channel name"""
        for cat in server_cats:
            if cat in gcrequest.lower():
                category = cat
        if category:
            category_remove = re.compile(re.escape(category), re.IGNORECASE)
            channel_suffix = category_remove.sub('', gcrequest)

        data['category'] = category
        data['channel_suffix'] = channel_suffix
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

    @acupdate.error 
    async def acupdate_handler(self, ctx, error):
        """
        """
        embed = discord.Embed(
            title = 'AutoChannel error',
            colour = discord.Colour.red()
        )
        msg = error

        if isinstance(error, commands.MissingPermissions):
            embed.title = 'Insufficient permissions'
            msg = 'Contact an admin for help.'
        if isinstance(error, commands.CommandInvokeError):
            embed.titls = 'Insufficent permissions'
            msg = 'Server is setup incorrect for mange_channel permissions for Auto-chan'
            
        embed.add_field(name='Error', value=msg)
        await ctx.send(embed=embed)

    @vc.error 
    async def ac_handler(self, ctx, error):
        """
        """
        embed = discord.Embed(
            title = 'AutoChannel error',
            colour = discord.Colour.red()
        )
        msg = error

        if isinstance(error, ACUnknownCategory):
            existing_cats = self.cat_names(ctx)
            msg = f'**Unkown category:** How-To: `!vc <category> <name of channel>`   **Category list:** {existing_cats}'
        if isinstance(error, VCProfaneWordused):
            msg = 'Auto-chan hates bad words, please be nice'
            
        embed.add_field(name='Error', value=msg)
        await ctx.send(embed=embed)


def setup(autochannel):
    """
    """
    autochannel.add_cog(AutoChannels(autochannel))
