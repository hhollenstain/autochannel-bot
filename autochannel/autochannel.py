import discord
import logging
import os
import asyncio
import aiohttp
import json
from discord.ext.commands import Bot
"""monitor"""

"""data"""
from autochannel.data.database import DB

log = logging.getLogger('discord')

class AutoChannel(discord.ext.commands.Bot):
    """A modified discord.Client class

    This mod dispatches most events to the different plugins.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db = DB()
        self.session = db.session()
        self.app_id = kwargs.get('app_id')
        self.auto_channel_prefix = kwargs.get('auto_channel_prefix')
        self.auto_categories = kwargs.get('auto_categories')
        self.dbl_token = kwargs.get('dbl_token')
        self.env = kwargs.get('env') or 'dev'
        self.dbl_token = kwargs.get('dbl_token')
        self.stats = None
        self.voice_channel_prefix = kwargs.get('voice_channel_prefix')