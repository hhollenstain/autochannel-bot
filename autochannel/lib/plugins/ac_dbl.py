"""Top.gg guild count posting (replaces legacy dblpy)."""
import asyncio
import logging

import topgg
from discord.ext import commands

LOG = logging.getLogger(__name__)


class TopGGPostCog(commands.Cog):
    """Posts guild count to Top.gg periodically when ``DBL_TOKEN`` is set."""

    def __init__(self, bot):
        self.bot = bot
        self._task: asyncio.Task | None = None
        self._client: topgg.DBLClient | None = None

    def cog_unload(self):
        if self._task and not self._task.done():
            self._task.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        token = self.bot.dbl_token
        if not token:
            LOG.info('Skipping Top.gg stats: no DBL_TOKEN')
            return
        if self._task is not None and not self._task.done():
            return
        self._client = topgg.DBLClient(token, default_bot_id=self.bot.user.id)
        self._task = asyncio.create_task(self._post_loop())

    async def _post_loop(self):
        assert self._client is not None
        while not self.bot.is_closed:
            try:
                kwargs = {'guild_count': len(self.bot.guilds)}
                if getattr(self.bot, 'shard_count', None):
                    kwargs['shard_count'] = self.bot.shard_count
                    kwargs['shard_id'] = self.bot.shard_id
                await self._client.post_guild_count(**kwargs)
                LOG.info('Posted guild count %s to Top.gg', len(self.bot.guilds))
            except Exception:
                LOG.exception('Failed to post guild count to Top.gg')
            await asyncio.sleep(1800)


async def setup(bot):
    await bot.add_cog(TopGGPostCog(bot))
