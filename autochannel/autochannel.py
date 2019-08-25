import discord
import logging
import os
import asyncio
import aiohttp
import json
from discord.ext.commands import Bot
from autochannel.lib.discordDog import DDAgent

log = logging.getLogger('discord')

class AutoChannel(discord.ext.commands.Bot):
    """A modified discord.Client class

    This mod dispatches most events to the different plugins.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_id = kwargs.get('app_id')
        self.auto_channel_prefix = kwargs.get('auto_channel_prefix')
        self.auto_categories = kwargs.get('auto_categories')
        self.dd_api_key = kwargs.get('dd_api_key')
        self.dd_app_key = kwargs.get('dd_app_key')
        self.env = kwargs.get('env') or 'dev'
        self.stats = None
        self.voice_channel_prefix = kwargs.get('voice_channel_prefix')

        if self.dd_api_key and self.dd_app_key:
           self.stats = DDAgent(dd_api_key=kwargs.get('dd_api_key'), dd_app_key=kwargs.get('dd_app_key'), constant_tags=[f'env:{self.env}', 'bot:autochannel'])
           self.stats.increment('autochannel_bot.start.count')