import traceback

from typing import Optional
import asyncio
import datetime
from unicodedata import category
import discord
import logging
import queue 
import random
import re
import time
from discord import app_commands
from discord.ext import commands
from profanityfilter import ProfanityFilter
"""AC imports"""
from autochannel.lib import utils
from autochannel.lib.metrics import command_metrics_counter, task_metrics_counter, queue_stats_gauge, COMMAND_SUMMARY_ACUPDATE
from autochannel.data.models import Guild, Category, Channel

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
    """[summary]
    
    Arguments:
        commands {[type]} -- [description]
    
    Raises:
        ACUnknownCategory: [description]
        VCProfaneWordused: [description]
        ACDisabledCustomCategory: [description]
    
    Returns:
        [type] -- [description]
    """
    def __init__(self, autochannel):
        self.autochannel = autochannel
        self.stats = autochannel.stats
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.autochannel.loop.create_task(self.queue_loop())
        self.autochannel.loop.create_task(self.loop_stats())

    async def loop_stats(self):
        """Loop to track event queue size"""
        while not self.autochannel.is_closed():
            LOG.debug(f'UPDATING QUEUE STATS {self.queue.qsize()}')
            queue_stats_gauge(self.queue.qsize())
            await asyncio.sleep(3)

    async def queue_loop(self):
        """Our main task loop."""
        await self.autochannel.wait_until_ready()

        while not self.autochannel.is_closed():
            LOG.info(f'QUEUE SIZE: {self.queue.qsize()}')
            await asyncio.sleep(.25)
            task = await self.queue.get()

            if not task.get('type'):
                self.autochannel.loop.call_soon_threadsafe(self.next.set)
                continue

            LOG.info(f'Running queue Task: {task}')
            try: 
                if task['type'] == 'ac_create_channel':
                    await self.ac_create_channel(task['cat'], 
                                                guild=task['guild'], 
                                                )

                if task['type'] == 'ac_delete_channel':
                    await self.ac_delete_channel(task['cat'], 
                                                guild=task['guild'], 
                                                force=task['force'],
                                                )

                if task['type'] == 'ac_prefix_sync':
                    await self.ac_prefix_sync(task['channel'],
                                            task['db_cat'],
                                            guild=task['guild'],
                                            )

            except Exception as e:
                LOG.error(e)

            self.autochannel.loop.call_soon_threadsafe(self.next.set)
            await self.next.wait()


    @task_metrics_counter
    async def ac_delete_channel(self, cat: discord.CategoryChannel, force: bool, **kwargs) -> None:
        """_summary_

        Args:
            cat (discord.CategoryChannel): _description_
            force (bool): _description_
        """        
        category = self.autochannel.session.query(Category).get(cat.id)
        db_channel_list_id = category.get_channels()
        if force:
            auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id]
            highest_empty_channel = self.ac_db_highest_empty_channel(auto_channels)
            LOG.debug(f'force deleting auto-channel: {highest_empty_channel.name}')
            await highest_empty_channel.delete(reason='Auto-chan keeping a tidy house')
        else:
            auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id and len(channel.members) < 1]
            LOG.debug(f'empty autochannels for {cat.name}: {auto_channels}')
            empty_channel_count = len(auto_channels)
            if empty_channel_count > category.empty_count:  
                highest_empty_channel = self.ac_db_highest_empty_channel(auto_channels)
                LOG.debug(f'deleting auto-channel: {highest_empty_channel.name}')
                await highest_empty_channel.delete(reason='Auto-chan keeping a tidy house')
            else:
                LOG.debug (f'GUILD: {cat.guild.name} CAT: {cat.name} : No more channels to clean up')           

    @task_metrics_counter
    async def ac_create_channel(self, cat: discord.CategoryChannel, **kwargs) -> Optional[discord.VoiceChannel]:
        """_summary_

        Args:
            cat (discord.CategoryChannel): _description_

        Returns:
            Optional[discord.VoiceChannel]: _description_
        """           
        db_cat = self.autochannel.session.query(Category).get(cat.id)
        db_channel_list_id = db_cat.get_channels()
        auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id]
        empty_channel_list = [channel for channel in auto_channels if  len(channel.members) < 1]
        """ need a list of empty channels to decide whatt to clean up """
        empty_channel_count = len(empty_channel_list)
        if empty_channel_count < db_cat.empty_count:
            channel_suffix = self.ac_db_channel_number(db_cat)
            LOG.debug(f' Channel created {db_cat.prefix}') 
            position = channel_suffix + len(cat.text_channels)
            chan_name = f'{db_cat.prefix} - {channel_suffix}'
            created_channel = await cat.create_voice_channel(chan_name, position=position, user_limit=db_cat.channel_size)
            LOG.debug(f'CHANNEL OBJECT CREATE => Channel(id={created_channel.id}, cat_id={cat.id}, type=voice)')
            chan_id_add = Channel(id=created_channel.id, cat_id=cat.id, chan_type='voice', num_suffix=channel_suffix)
            self.autochannel.session.add(chan_id_add)
            self.autochannel.session.commit()
        
        else:
            LOG.debug(f'Skipping channel AC create due to no longer needed')
            return None

        return created_channel

    @task_metrics_counter
    async def vc_delete_channel(self, voicechannel: discord.VoiceChannel, **kwargs) -> None:
        """_summary_

        Args:
            voicechannel (discord.VoiceChannel): _description_
        """
        reason = kwargs.get('reason')
        await voicechannel.delete(reason=reason)
        
    async def manage_auto_voice_channels(self, autochannel, guild=None) -> None:
        """_summary_

        Args:
            autochannel (_type_): _description_
            guild (_type_, optional): _description_. Defaults to None.
        """        
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
                    db_channel_list_id = db_cat.get_channels()
                    auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id]
                    for channel in auto_channels:
                        q_object = {
                                'cat': cat, 
                                'guild': server.name,
                                'type': 'ac_delete_channel',
                                'force': True,
                            }
                        LOG.debug(f'Adding to queue: {q_object}')
                        await self.queue.put(q_object)
            
            categories = [cat for cat in server.categories if cat.id in db_cats]
            """checking if the db knows about the categorey"""
            for cat in categories:
                self.autochannel.session.expire_all()
                db_cat = self.autochannel.session.query(Category).get(cat.id) 
                auto_channels = [channel for channel in cat.voice_channels if channel.name.startswith(db_cat.prefix)]
                """
                Temporary to sync non db entries
                be removed on the 6.1.x release
                """
                db_channel_list_id = db_cat.get_channels()
                missing_db_channels = [channel for channel in auto_channels if channel.id not in db_channel_list_id]
                LOG.debug(missing_db_channels)

                for chan in missing_db_channels:
                    try:
                        chan_id_add = Channel(id=chan.id, cat_id=db_cat.id, chan_type='voice', num_suffix=int(self.get_ac_channel(chan)))
                        self.autochannel.session.add(chan_id_add)
                    except:
                        LOG.info(f'skipping issue for: guild={server.name}, channel={chan.name}')
                        pass
                
                if len(missing_db_channels) > 0:
                    self.autochannel.session.commit()

                """
                be removed on the 6.1.x release
                """

                db_channel_list_id = db_cat.get_channels()
                auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id]
                
                """
                    Will sync outdated prefixes
                """
                prefix_sync = [channel for channel in auto_channels if not channel.name.startswith(db_cat.prefix)]
                for chan in prefix_sync:
                    q_object = {
                        'db_cat': db_cat, 
                        'channel': chan,
                        'guild': server.name, 
                        'type': 'ac_prefix_sync'
                    }
                    LOG.debug(f'Adding to queue: {q_object}')
                    await self.queue.put(q_object)

                empty_channel_list = [channel for channel in auto_channels if  len(channel.members) < 1]
                """ need a list of empty channels to decide wat to clean up """
                empty_channel_count = len(empty_channel_list)
                LOG.debug(f'GUILD: {server.name} category: {cat.name} empty channel count {empty_channel_count}')

                """
                Adding new channels in queue to be processed
                """
                if empty_channel_count < db_cat.empty_count:
                    while empty_channel_count < db_cat.empty_count:
                        q_object = {
                                'cat': cat, 
                                'guild': server.name, 
                                'type': 'ac_create_channel'
                            }
                        LOG.debug(f'Adding to queue: {q_object}')
                        await self.queue.put(q_object)
                        empty_channel_count += 1


                if empty_channel_count > 1:
                    while empty_channel_count > db_cat.empty_count:
                        q_object = {
                                'cat': cat, 
                                'guild': server.name, 
                                'type': 'ac_delete_channel',
                                'force': True,
                            }
                        LOG.debug(f'Adding to queue: {q_object}')
                        await self.queue.put(q_object)
                        empty_channel_count -= 1

    @task_metrics_counter
    async def ac_prefix_sync(self, channel, db_cat, **kwargs):
        """[summary]
        
        Arguments:
            channel {[voice channel object]} -- Channel object to update
            db_cat {[Category db object]} -- category db object 
        """
        channel_db = self.autochannel.session.query(Channel).get(channel.id)
        LOG.debug(f'Channel suffix being updated: {channel_db.num_suffix}')
        await channel.edit(name=f'{db_cat.prefix} - {channel_db.num_suffix}')

    def ac_db_highest_empty_channel(self, empty_auto_channels: list) -> Optional[discord.VoiceChannel]:
        """_summary_

        Args:
            empty_auto_channels (list): _description_

        Returns:
            Optional[discord.VoiceChannel]: _description_
        """        
        highest_empty_channel = None
        highest_empty_channel_num = None
        for ec in empty_auto_channels:
            ec_db = self.autochannel.session.query(Channel).get(ec.id)
            if not highest_empty_channel:
                highest_empty_channel_num = self.get_ac_db_channel(ec_db)
                highest_empty_channel = ec
            if self.get_ac_db_channel(ec_db) > highest_empty_channel_num:
                        highest_empty_channel = ec
        return highest_empty_channel

    @commands.Cog.listener()
    async def on_ready(self):
        """
        on_ready by default will run when the bot is ready. This does some
        tasks incase the bot is down when users leave channels empty
        """
        await self.manage_auto_voice_channels(self.autochannel)

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.command(name="sync", description="sync from http://auto-chan.io")
    @command_metrics_counter
    async def sync(self, interaction: discord.Interaction) -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
        """
        await self.manage_auto_voice_channels(self.autochannel, guild=interaction.guild)
        await interaction.response.send_message("Changes have been syncronized from http://auto-chan.io/")


    @sync.error 
    async def on_sync_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            error (app_commands.AppCommandError): _description_
        """
        await interaction.response.send_message(f"Error {error}")

    @app_commands.describe(category='name of category', channel_name='custom name of channel')
    @app_commands.command(name="vc", description="create voice channel")
    @command_metrics_counter
    async def vc(self, interaction: discord.Interaction, category: str, channel_name: str = '') -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            category (str): _description_
            channelname (str, optional): _description_. Defaults to ''.

        Raises:
            ACUnknownCategory: _description_
            VCProfaneWordused: _description_
            ACDisabledCustomCategory: _description_
        """ 
        if not self.validateCategory(interaction, category):
            raise ACUnknownCategory(f'Unknown Discord category')

        category_name = [cat for cat in interaction.guild.categories if cat.name.lower() in category.lower()][0]
        category_obj = self.autochannel.session.query(Category).get(category_name.id)

        """Checks if there is channel name and if there is profanity used"""
        if channel_name:
            vc_suffix = channel_name
            if pf.is_profane(channel_name):
                raise VCProfaneWordused(f'Used a profane word when creating a custom voice channel')
        else:
            vc_suffix = self.vc_channel_number(interaction, category, category_obj)
        
        if not category_obj.custom_enabled:
            raise ACDisabledCustomCategory(f'Category {category_name.name} is disabled. To use custom channels in this category an **ADMIN** must enable:  http://auto-chan.io')

        created_vc= await interaction.guild.create_voice_channel(f'{category_obj.custom_prefix} {vc_suffix}', overwrites={}, category=category_name, reason='AutoChannel bot automation')
        invite_link = await self.createVCInvite(interaction, created_vc)

        await interaction.channel.send(f'AutoChannel made `{interaction.user}` a channel `{created_vc.name}`')
        await interaction.response.send_message(invite_link)

        await asyncio.sleep(60)
        if  len(created_vc.members) < 1:
            try:
                await self.vc_delete_channel(created_vc, reason='No one joined the custom channel after 60 seconds')
            except:
                """annoying to see this error doesn't add value to the end user"""
                pass


    @vc.autocomplete('category')
    async def vc_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            current (str): _description_

        Returns:
            list[app_commands.Choice[str]]: _description_
        """

        """good chance this might cause lots of db queries if abused"""
        category_objs = self.autochannel.session.query(Category).filter_by(custom_enabled=True, guild_id=interaction.guild.id).all()
 
        categories = []
        for category in category_objs:
            try:
                categories.append(interaction.guild.get_channel(category.id).name)
            except Exception as e:
                LOG.error(e)

        return [
            app_commands.Choice(name=category, value=category)
            for category in categories if current.lower() in category.lower()
        ]

    @vc.error 
    async def on_vc_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            error (app_commands.AppCommandError): _description_
        """        
        msg = error
        if isinstance(error, ACUnknownCategory):
            existing_cats = self.cat_names(ctx)
            msg += f'**Unknown category:** How-To: `!vc <category> <name of channel>`   **Category list:** {existing_cats}'
        if isinstance(error, VCProfaneWordused):
            msg += 'Auto-chan hates bad words, please be nice'
            
        traceback.print_exc()
        await interaction.response.send_message(msg)


    def valid_auto_channel(self, v_state: discord.VoiceState) -> bool:
        """_summary_

        Args:
            v_state (discord.VoiceState): _description_

        Returns:
            bool: _description_
        """        
        if(
                v_state is not None and
                v_state.channel is not None and
                v_state.channel.category is not None

          ):       
            category = self.autochannel.session.query(Category).get(v_state.channel.category.id)
            if category:
                db_channel_list_id = category.get_channels()
            else:
                db_channel_list_id = []
            if (
                    category and 
                    category.enabled and 
                    v_state.channel.id in db_channel_list_id
                ):
                return True
            else:
                return False
        else:
            return False

    async def after_ac_task(self, after: discord.VoiceState, member=None) -> None:
        """_summary_

        Args:
            after (discord.VoiceState): _description_
            member (_type_, optional): _description_. Defaults to None.
        """        
        cat = after.channel.category
        category = self.autochannel.session.query(Category).get(cat.id)
        db_channel_list_id = category.get_channels()
        auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id]
        empty_channel_count = len([channel for channel in auto_channels if  len(channel.members) < 1])
        if empty_channel_count < category.empty_count:
            q_object = {
                'cat': cat, 
                'guild': cat.guild.name, 
                'type': 'ac_create_channel'
            }
            LOG.debug(f'queue object added: {q_object}')
            await self.queue.put(q_object)
            

    async def before_ac_task(self, before: discord.VoiceState, member=None) -> None:
        """handles the updates to the old channel the user left

        Args:
            before (discord.VoiceState): before state channel
            member (_type_, optional): _description_. Defaults to None.
        """        
        cat = before.channel.category
        category = self.autochannel.session.query(Category).get(cat.id)
        db_channel_list_id = category.get_channels()
        if len(before.channel.members) < 1:
            auto_channels = [channel for channel in cat.voice_channels if channel.id in db_channel_list_id and len(channel.members) < 1]
            LOG.debug(f'empty autochannels for {cat.name}: {auto_channels}')
            empty_channel_count = len(auto_channels)
            if empty_channel_count > category.empty_count:
                q_object = {
                        'cat': cat, 
                        'guild': cat.guild.name, 
                        'type': 'ac_delete_channel',
                        'force': False,
                    }
                LOG.debug(f'queue object added: {q_object}')
                await self.queue.put(q_object)

    @task_metrics_counter
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel) -> None:
        """This tracks all channel deletes and if the channel is tracked by auto-chan, 
           it will clean up the db entry. This is imporant due to admins deleting channels managed by auto-chan
           that otherwise would get missed.
        
        Arguments:
            channel {[type]} -- [description]
        """

        LOG.debug(f'Channel that was deleted {channel.id}')
        chan_id_delete = self.autochannel.session.query(Channel).get(channel.id)
        if chan_id_delete:
            LOG.debug(f'chan_ID_DELETE: {chan_id_delete}')
            self.autochannel.session.delete(chan_id_delete)
            self.autochannel.session.commit()

    @task_metrics_counter
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """Checks before and afer states of channels users leave and join
        this will handle logic to make sure there is no more than N (current
        defaulted to 1) empty channel at any time. This will also create a
        if less than N (current set to 1).

        Args:
            member (discord.Member): discord member
            before (discord.VoiceState): before voice channel object 
            after (discord.VoiceState): after voice channel object
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

    def ac_db_channel_number(self, db_cat) -> int:
        """returns number from auto prefix and returns the lowest number 

        Args:
            db_cat (_type_): List of voice_channels objects 

        Returns:
            int: the lowest number missing from the sequence of voice_channels
        """        
        suffix_list = db_cat.get_chan_suffix()

        return utils.missing_numbers(suffix_list)[0]

    def get_ac_channel(self, auto_channel) -> int:
        """returns the auto generated number suffix of a channel

        Args:
            auto_channel (_type_): _description_

        Returns:
            int: _description_
        """        
        return int(''.join(auto_channel.name.split(' ')[-1:]))

    def get_ac_db_channel(self, auto_channel):
        """[summary]
        
        Arguments:
            auto_channel {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        return auto_channel.num_suffix

    def vc_channel_number(self, interaction: discord.Interaction, category, category_obj) -> int:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            category (_type_): _description_
            categoryObj (_type_): _description_

        Returns:
            int: _description_
        """        
        ac_channels = [vc for vc in interaction.guild.voice_channels if str(vc.category).lower().startswith(f'{category}') and vc.name.startswith(category_obj.custom_prefix)]
        return (len(ac_channels) + 1)

    async def createVCInvite(self, interaction: discord.Interaction, voiceChannel) -> discord.Invite:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            voiceChannel (_type_): _description_

        Returns:
            discord.Invite: _description_
        """            
        invitelink = await voiceChannel.create_invite(reason='AutoChannel likes to make links')
        return invitelink

    def validateCategory(self, interaction: discord.Interaction, category: str) -> bool:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            category (str): _description_

        Returns:
            bool: _description_
        """        
        serverCatagories = self.getGuildCategories(interaction)

        LOG.debug(f'Categories found: {serverCatagories}')

        """ Checking to see if category is in the string of data everything else is channel name"""
        for cat in serverCatagories:
            if cat in category.lower():
                return True
        
        return False

    def getGuildCategories(self, interaction: discord.Interaction) -> list:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_

        Returns:
            list: _description_
        """        
        cat_list = []
        for cat in interaction.guild.categories:
            cat_list.append(cat.name.lower())
        return cat_list




async def setup(autochannel):
    """_summary_

    Args:
        autochannel (_type_): _description_
    """    
    await autochannel.add_cog(AutoChannels(autochannel))
