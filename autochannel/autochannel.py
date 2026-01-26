import discord
import logging
import os
import asyncio
import aiohttp
import json
from discord.ext.commands import Bot

"""data"""
from autochannel.data.database import DB

log = logging.getLogger('discord')

class AutoChannel(discord.ext.commands.Bot):
    """A modified discord.Client class

    This mod dispatches most events to the different plugins.

    """

    def __init__(self, *args,initial_extensions: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.db = DB()
        self.session = self.db.session()
        self.app_id = kwargs.get('app_id')
        self.auto_channel_prefix = kwargs.get('auto_channel_prefix')
        self.auto_categories = kwargs.get('auto_categories')
        self.dbl_token = kwargs.get('dbl_token')
        self.env = kwargs.get('env') or 'dev'
        self.dbl_token = kwargs.get('dbl_token')
        self.stats = None
        self.voice_channel_prefix = kwargs.get('voice_channel_prefix')
        self.initial_extensions = initial_extensions
        self.testing_guild_id = kwargs.get('testing_guild_id') or None
    
    def _ensure_session(self):
        """Ensure the session is in a valid state, rollback if needed.
        This prevents PendingRollbackError by clearing any invalid transactions.
        """
        try:
            # Rollback is idempotent - safe to call even if no transaction exists
            # This clears any pending rollback state
            self.session.rollback()
        except Exception as e:
            # If rollback fails, the session is completely invalid - create a new one
            log.warning(f"Session invalid, creating new session: {e}")
            try:
                self.session.close()
            except Exception:
                pass
            self.session = self.db.session()

    async def setup_hook(self) -> None:
        """_summary_
        """
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)
            log.info(f'Commands successfully updated to GUILD: {guild.id}')
        else:
            await self.tree.sync()
