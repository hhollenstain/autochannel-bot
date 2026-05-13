#!/usr/bin/env python3
"""
Tamago BOT LIVES!
"""
import asyncio
import logging
import os

import coloredlogs
import discord
from prometheus_client import start_http_server

from autochannel.autochannel import AutoChannel
from autochannel.lib import utils

EXTENSIONS = [
    'autochannel.lib.plugins.autochannels',
    'autochannel.lib.plugins.ac_dbl',
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
_auto_cat = os.getenv('AUTO_CATEGORIES') or 'auto-voice'
AUTO_CATEGORIES = [c.strip() for c in _auto_cat.lower().split(',') if c.strip()]
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
    intents.message_content = True  # prefix commands (!autochannel, etc.)
    intents.members = True  # user counts / member-aware features
    LOG.info('Intents: %s', intents)
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
