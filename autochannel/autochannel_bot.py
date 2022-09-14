#!/usr/bin/env python3
"""
Tamago BOT LIVES!
"""
import asyncio
import random
import os
import discord
import importlib
import logging
import coloredlogs
import sys
from discord import Game
from discord.ext import commands
from discord.ext.commands import Bot
"""metrics"""
from prometheus_client import start_http_server
"""AC Imports"""
from autochannel.lib import utils
from autochannel.autochannel import AutoChannel
from autochannel.data.models import Guild, Category

EXTENSIONS = [
    'autochannel.lib.plugins.autochannels',
    # 'autochannel.lib.plugins.ac_dbl', broken requires some fixes
    'autochannel.lib.plugins.join',
    'autochannel.lib.plugins.server',
    ]

LOG = logging.getLogger(__name__)

APP_ID = os.getenv('APP_ID') or 'fakeid'
BOT_PREFIX = ("?", "!")
DBL_TOKEN = os.getenv('DBL_TOKEN') or None
SHARD = os.getenv('SHARD') or 0
SHARD_COUNT = os.getenv('SHARD_COUNT') or 1
TOKEN = os.getenv('TOKEN')
VOICE_CHANNEL_PREFIX = os.getenv('VOICE_CHANNEL_PREFIX') or '!VC '
AUTO_CHANNEL_PREFIX = os.getenv('AUTO_CHANNEL_PREFIX') or '!AC '
AUTO_CATEGORIES = os.getenv('AUTO_CATEGORIES').lower().split(",") or ['auto-voice']
TESTING_GUILD_ID = os.getenv('TESTING_GUILD_ID')
ENV = os.getenv('ENV') or None

def main():
    """_summary_
    """
    asyncio.run(runAC())

async def runAC():
    """Entrypoint if called as an executable."""
    args = utils.parse_arguments()
    logging.basicConfig(level=logging.INFO)
    coloredlogs.install(level=0,
                        fmt="[%(asctime)s][%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                        isatty=True)
    if args.debug:
        l_level = logging.DEBUG
    else:
        l_level = logging.INFO

    logging.getLogger(__package__).setLevel(l_level)
    logging.getLogger('discord').setLevel(l_level)
    logging.getLogger('websockets.protocol').setLevel(l_level)
    logging.getLogger('urllib3').setLevel(l_level)

    LOG.info("LONG LIVE AutoChannel bot")
    intents = discord.Intents.default()
    LOG.info(f'Intents: {intents}')
    autochannel = AutoChannel(
                    shard_id=int(SHARD), 
                    shard_count=int(SHARD_COUNT),
                    command_prefix=BOT_PREFIX, 
                    app_id=APP_ID, 
                    voice_channel_prefix=VOICE_CHANNEL_PREFIX,
                    auto_channel_prefix=AUTO_CHANNEL_PREFIX, 
                    auto_categories=AUTO_CATEGORIES,
                    env=ENV, 
                    dbl_token=DBL_TOKEN, 
                    intents=intents, 
                    initial_extensions=EXTENSIONS,
                    testing_guild_id=TESTING_GUILD_ID,
                    )

    start_http_server(8000)
    await autochannel.start(TOKEN)
   


if __name__ == '__main__':
    main()
