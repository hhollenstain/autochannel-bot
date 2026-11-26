"""AutoChannels cog for managing automatic voice channel creation."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time

import discord
from autochannel_db import Category, Channel
from discord import app_commands
from discord.ext import commands
from profanityfilter import ProfanityFilter
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from autochannel.autochannel import AutoChannel
from autochannel.lib.maintenance import (
    CategorySnapshot,
    channels_to_create,
    channels_to_delete,
    next_suffixes,
)
from autochannel.lib.metrics import (
    command_metrics_counter,
    queue_stats_gauge,
    task_metrics_counter,
)

LOG = logging.getLogger(__name__)
pf = ProfanityFilter(no_word_boundaries=True)

# How long a freshly created channel is counted as "pending" while we wait for
# the gateway CHANNEL_CREATE event to add it to the cache.
PENDING_CHANNEL_TTL: float = 30.0
TIDY_REASON = "Auto-chan keeping a tidy house"


class ACMissingChannel(commands.CommandError):
    """Custom exception for missing channel errors."""


class ACUnknownCategory(app_commands.AppCommandError):
    """Raised when ``/vc`` is given a category that does not exist."""


class ACDisabledCustomCategory(app_commands.AppCommandError):
    """Raised when ``/vc`` targets a category with custom channels disabled."""


class VCProfaneWordused(app_commands.AppCommandError):
    """Raised when a custom channel name contains profanity."""


class AutoChannels(commands.Cog):
    """Cog for managing automatic voice channel creation and deletion.

    Every category the bot manages is kept at ``empty_count`` empty auto
    channels. Voice state changes and ``/sync`` enqueue a category for
    reconciliation; a single background worker processes the queue serially so
    Discord rate limits are respected and concurrent events cannot race each
    other into creating or deleting too many channels.
    """

    def __init__(self, autochannel: AutoChannel) -> None:
        """Initialize the AutoChannels cog.

        Args:
            autochannel: The AutoChannel bot instance.
        """
        self.autochannel = autochannel
        self.queue: asyncio.Queue[discord.CategoryChannel] = asyncio.Queue()
        self._queued_categories: set[int] = set()
        # channel id -> (category id, monotonic creation time)
        self._pending_channels: dict[int, tuple[int, float]] = {}
        self._tasks: list[asyncio.Task[None]] = []

    async def cog_load(self) -> None:
        """Start the queue worker and queue metrics background tasks."""
        self._tasks = [
            asyncio.create_task(self.queue_loop(), name="autochannels-queue"),
            asyncio.create_task(self.loop_stats(), name="autochannels-stats"),
        ]

    async def cog_unload(self) -> None:
        """Cancel the background tasks started in :meth:`cog_load`."""
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def loop_stats(self) -> None:
        """Background task to track event queue size and update metrics."""
        while not self.autochannel.is_closed():
            queue_stats_gauge(self.queue.qsize())
            await asyncio.sleep(3)

    async def queue_loop(self) -> None:
        """Background worker that reconciles queued categories one at a time."""
        await self.autochannel.wait_until_ready()

        while not self.autochannel.is_closed():
            cat = await self.queue.get()
            # Allow new events to re-queue this category while it is processed.
            self._queued_categories.discard(cat.id)
            try:
                current = cat.guild.get_channel(cat.id)
                if isinstance(current, discord.CategoryChannel):
                    await self.ac_reconcile_category(current)
            except Exception:
                LOG.exception("Failed to reconcile category %s in %s", cat.id, cat.guild.name)
            finally:
                self.queue.task_done()

    def enqueue_category(self, cat: discord.CategoryChannel) -> None:
        """Queue a category for reconciliation unless it is already queued.

        Args:
            cat: The category to reconcile.
        """
        if cat.id in self._queued_categories:
            return
        self._queued_categories.add(cat.id)
        LOG.debug("Queueing reconcile for GUILD: %s CAT: %s", cat.guild.name, cat.name)
        self.queue.put_nowait(cat)

    def load_category(self, cat_id: int) -> CategorySnapshot | None:
        """Load a category's configuration and tracked channels from the database.

        Args:
            cat_id: Discord category ID.

        Returns:
            A detached snapshot, or None if the category is not configured.
        """
        with self.autochannel.db.transaction() as session:
            category = session.get(Category, cat_id, options=[selectinload(Category.channels)])
            return None if category is None else CategorySnapshot.from_model(category)

    def load_categories(self, guild_id: int | None = None) -> dict[int, CategorySnapshot]:
        """Load every configured category, optionally limited to one guild.

        Args:
            guild_id: Restrict to this guild, or None for all guilds.

        Returns:
            Mapping of category ID to snapshot.
        """
        stmt = select(Category).options(selectinload(Category.channels))
        if guild_id is not None:
            stmt = stmt.where(Category.guild_id == guild_id)
        with self.autochannel.db.transaction() as session:
            return {
                category.id: CategorySnapshot.from_model(category)
                for category in session.scalars(stmt)
            }

    def track_channel(self, channel_id: int, cat_id: int, suffix: int) -> None:
        """Record a newly created auto channel in the database.

        Args:
            channel_id: Discord channel ID.
            cat_id: Discord category ID.
            suffix: Numeric suffix assigned to the channel.
        """
        with self.autochannel.db.transaction() as session:
            session.add(Channel(id=channel_id, cat_id=cat_id, chan_type="voice", num_suffix=suffix))

    def untrack_channels(self, channel_ids: list[int]) -> None:
        """Remove auto channel rows from the database.

        Args:
            channel_ids: Discord channel IDs to forget.
        """
        if not channel_ids:
            return
        with self.autochannel.db.transaction() as session:
            session.execute(delete(Channel).where(Channel.id.in_(channel_ids)))

    def pending_channel_count(self, cat: discord.CategoryChannel) -> int:
        """Count channels we created that are not yet visible in the cache.

        Entries are dropped once the channel shows up in the cache or after
        :data:`PENDING_CHANNEL_TTL` seconds.

        Args:
            cat: The category to count pending channels for.

        Returns:
            Number of pending (and therefore empty) channels in the category.
        """
        now = time.monotonic()
        count = 0
        for channel_id, (cat_id, created) in list(self._pending_channels.items()):
            if cat.guild.get_channel(channel_id) is not None or now - created > PENDING_CHANNEL_TTL:
                del self._pending_channels[channel_id]
            elif cat_id == cat.id:
                count += 1
        return count

    @task_metrics_counter
    async def ac_reconcile_category(self, cat: discord.CategoryChannel) -> None:
        """Bring a category to its configured number of empty auto channels.

        Creates channels when there are too few empty ones, deletes the
        highest-numbered empty channels when there are too many (all of them
        when the category is disabled) and renames channels whose prefix is out
        of date.

        Args:
            cat: The category to reconcile.
        """
        snapshot = self.load_category(cat.id)
        if snapshot is None:
            return

        tracked = [channel for channel in cat.voice_channels if channel.id in snapshot.channels]
        empty = [channel for channel in tracked if not channel.members]
        pending = self.pending_channel_count(cat)
        target = snapshot.target_empty

        to_delete = channels_to_delete(
            [channel.id for channel in empty], snapshot.channels, target, pending
        )
        for channel_id in to_delete:
            surplus = cat.guild.get_channel(channel_id)
            # Re-check: a member may have joined while earlier deletes were awaited.
            if not isinstance(surplus, discord.VoiceChannel) or surplus.members:
                continue
            LOG.debug("Deleting auto-channel %s in %s", surplus.name, cat.guild.name)
            with contextlib.suppress(discord.NotFound):
                await surplus.delete(reason=TIDY_REASON)
            self.untrack_channels([channel_id])

        missing = channels_to_create(len(empty) + pending, target)
        for suffix in next_suffixes(snapshot.channels.values(), missing):
            await self.create_auto_channel(cat, snapshot, suffix)

        if snapshot.enabled:
            for channel in tracked:
                if not channel.name.startswith(snapshot.prefix):
                    await self.ac_prefix_sync(channel, snapshot)

    async def create_auto_channel(
        self, cat: discord.CategoryChannel, snapshot: CategorySnapshot, suffix: int
    ) -> discord.VoiceChannel | None:
        """Create and track a single auto voice channel.

        Args:
            cat: Category to create the channel in.
            snapshot: The category's configuration.
            suffix: Numeric suffix for the new channel.

        Returns:
            The created channel, or None if it could not be tracked.
        """
        created = await cat.create_voice_channel(
            snapshot.channel_name(suffix),
            position=suffix + len(cat.text_channels),
            user_limit=snapshot.channel_size,
            reason="AutoChannel bot automation",
        )
        LOG.debug("Created auto-channel %s (%s) in CAT: %s", created.name, created.id, cat.id)
        try:
            self.track_channel(created.id, cat.id, suffix)
        except Exception:
            LOG.exception("Could not track channel %s; removing it", created.id)
            with contextlib.suppress(discord.HTTPException):
                await created.delete(reason="AutoChannel could not track this channel")
            return None
        self._pending_channels[created.id] = (cat.id, time.monotonic())
        return created

    @task_metrics_counter
    async def vc_delete_channel(
        self, voicechannel: discord.VoiceChannel | discord.StageChannel, reason: str | None = None
    ) -> None:
        """Delete a custom voice channel.

        Args:
            voicechannel: The voice channel to delete.
            reason: Audit log reason for the deletion.
        """
        await voicechannel.delete(reason=reason)

    async def manage_auto_voice_channels(
        self, autochannel: AutoChannel, guild: discord.Guild | None = None
    ) -> None:
        """Re-sync auto channels with the database and queue every category.

        Removes database rows for auto channels that no longer exist (deleted
        while the bot was offline) and queues each configured category that is
        enabled, or that is disabled but still has auto channels to clean up.

        Args:
            autochannel: The bot instance.
            guild: The guild to manage channels in; if None manage all guilds.
        """
        snapshots = self.load_categories(guild.id if guild else None)
        guilds = [guild] if guild else list(autochannel.guilds)

        for server in guilds:
            if server.unavailable:
                continue
            for cat in server.categories:
                snapshot = snapshots.get(cat.id)
                if snapshot is None:
                    continue
                present = {channel.id for channel in cat.voice_channels}
                stale = [cid for cid in snapshot.channels if cid not in present]
                if stale:
                    LOG.info("Forgetting %d stale auto-channels in CAT: %s", len(stale), cat.id)
                    self.untrack_channels(stale)
                if snapshot.enabled or len(stale) < len(snapshot.channels):
                    self.enqueue_category(cat)

    @task_metrics_counter
    async def ac_prefix_sync(
        self, channel: discord.VoiceChannel, snapshot: CategorySnapshot
    ) -> None:
        """Rename a channel to match the category's current prefix.

        Args:
            channel: The voice channel to rename.
            snapshot: The category's configuration.
        """
        suffix = snapshot.channels.get(channel.id)
        if suffix is None:
            return
        LOG.debug("Renaming auto-channel %s to prefix %s", channel.id, snapshot.prefix)
        await channel.edit(name=snapshot.channel_name(suffix))

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Re-sync voice channels in case anything changed while the bot was down."""
        await self.manage_auto_voice_channels(self.autochannel)

    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.command(name="sync", description="sync from http://auto-chan.io")
    @command_metrics_counter
    async def sync(self, interaction: discord.Interaction) -> None:
        """Queue every configured category in this guild for reconciliation.

        Args:
            interaction: The interaction that triggered the command.
        """
        await self.manage_auto_voice_channels(self.autochannel, guild=interaction.guild)
        await interaction.response.send_message(
            "Changes have been syncronized from http://auto-chan.io/"
        )

    @sync.error
    async def on_sync_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Report ``/sync`` failures back to the user.

        Args:
            interaction: The interaction that triggered the command.
            error: The error raised by the command.
        """
        LOG.exception("sync command failed: %s", error)
        msg = f"Error {error}"
        if interaction.response.is_done():
            await interaction.followup.send(msg)
        else:
            await interaction.response.send_message(msg)

    @app_commands.describe(category="name of category", channel_name="custom name of channel")
    @app_commands.command(name="vc", description="create voice channel")
    @command_metrics_counter
    async def vc(
        self, interaction: discord.Interaction, category: str, channel_name: str = ""
    ) -> None:
        """Create a temporary custom voice channel and reply with an invite.

        The channel is deleted after 60 seconds if nobody joins, or as soon as
        it becomes empty afterwards.

        Args:
            interaction: The interaction that triggered the command.
            category: Name of the category to create the channel in.
            channel_name: Optional custom channel name.

        Raises:
            ACUnknownCategory: The category does not exist or is not configured.
            VCProfaneWordused: The channel name contains profanity.
            ACDisabledCustomCategory: Custom channels are disabled for the category.
        """
        guild = interaction.guild
        if guild is None or not self.validateCategory(interaction, category):
            raise ACUnknownCategory("Unknown Discord category")

        discord_category = next(
            cat for cat in guild.categories if cat.name.lower() in category.lower()
        )
        snapshot = self.load_category(discord_category.id)
        if snapshot is None:
            raise ACUnknownCategory("Unknown Discord category")

        vc_suffix: str | int
        if channel_name:
            vc_suffix = channel_name
            if pf.is_profane(channel_name):
                raise VCProfaneWordused("Used a profane word when creating a custom voice channel")
        else:
            vc_suffix = self.vc_channel_number(interaction, category, snapshot)

        if not snapshot.custom_enabled:
            raise ACDisabledCustomCategory(
                f"Category {discord_category.name} is disabled. "
                f"ADMIN** must enable: http://auto-chan.io"
            )

        created_vc = await guild.create_voice_channel(
            f"{snapshot.custom_prefix} {vc_suffix}",
            overwrites={},
            category=discord_category,
            reason="AutoChannel bot automation",
        )
        invite_link = await self.createVCInvite(interaction, created_vc)

        await interaction.response.send_message(str(invite_link))
        if isinstance(interaction.channel, discord.abc.Messageable):
            await interaction.channel.send(
                f"AutoChannel made `{interaction.user}` a channel `{created_vc.name}`"
            )

        await asyncio.sleep(60)
        if not created_vc.members:
            with contextlib.suppress(discord.HTTPException):
                await self.vc_delete_channel(
                    created_vc, reason="No one joined the custom channel after 60 seconds"
                )

    @vc.autocomplete("category")
    async def vc_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Suggest categories in this guild that allow custom channels.

        Args:
            interaction: The autocomplete interaction.
            current: What the user has typed so far.

        Returns:
            Matching category choices (Discord shows at most 25).
        """
        guild = interaction.guild
        if guild is None:
            return []

        with self.autochannel.db.transaction() as session:
            category_ids = list(
                session.scalars(
                    select(Category.id).where(
                        Category.custom_enabled.is_(True), Category.guild_id == guild.id
                    )
                )
            )

        names = [
            channel.name for cid in category_ids if (channel := guild.get_channel(cid)) is not None
        ]
        return [
            app_commands.Choice(name=name, value=name)
            for name in names
            if current.lower() in name.lower()
        ][:25]

    @vc.error
    async def on_vc_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Report ``/vc`` failures back to the user with a helpful hint.

        Args:
            interaction: The interaction that triggered the command.
            error: The error raised by the command.
        """
        LOG.exception("vc command failed: %s", error)
        msg = str(error)
        if isinstance(error, ACUnknownCategory):
            existing_cats = ", ".join(self.getGuildCategories(interaction))
            msg = (
                f"{msg} **Unknown category:** How-To: `/vc <category> <name of channel>` "
                f"**Category list:** {existing_cats}"
            )
        elif isinstance(error, VCProfaneWordused):
            msg += " Auto-chan hates bad words, please be nice"
        if interaction.response.is_done():
            await interaction.followup.send(msg)
        else:
            await interaction.response.send_message(msg)

    @task_metrics_counter
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        """Forget deleted auto channels and refill their category.

        Admins can delete auto channels by hand; without this the database
        would keep stale rows and the category could end up with no empty
        channel.

        Args:
            channel: The deleted channel.
        """
        self._pending_channels.pop(channel.id, None)
        with self.autochannel.db.transaction() as session:
            tracked = session.get(Channel, channel.id)
            if tracked is None:
                return
            LOG.debug("Forgetting deleted auto-channel %s", channel.id)
            session.delete(tracked)
        if channel.category is not None:
            self.enqueue_category(channel.category)

    @task_metrics_counter
    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ) -> None:
        """React to members joining, leaving or moving between voice channels.

        Empty custom ``/vc`` channels are deleted, and any auto channel category
        the member left or joined is queued for reconciliation so it keeps
        ``empty_count`` empty channels available. Mute/deafen/stream updates
        that don't change channel are ignored.

        Args:
            member: The member whose voice state changed.
            before: The voice state before the update.
            after: The voice state after the update.
        """
        before_channel, after_channel = before.channel, after.channel
        if before_channel == after_channel:
            return

        for channel in (before_channel, after_channel):
            if channel is None or channel.category is None:
                continue
            snapshot = self.load_category(channel.category.id)
            if snapshot is None:
                continue
            if channel.id in snapshot.channels:
                self.enqueue_category(channel.category)
            elif (
                channel is before_channel
                and isinstance(channel, discord.VoiceChannel | discord.StageChannel)
                and not channel.members
                and channel.name.startswith(snapshot.custom_prefix)
            ):
                with contextlib.suppress(discord.NotFound):
                    await self.vc_delete_channel(channel, reason="now empty")

    def vc_channel_number(
        self, interaction: discord.Interaction, category: str, snapshot: CategorySnapshot
    ) -> int:
        """Return the next number for an unnamed custom ``/vc`` channel.

        Args:
            interaction: The interaction that triggered the command.
            category: The category name the user asked for.
            snapshot: The category's configuration.

        Returns:
            One more than the number of existing custom channels in the category.
        """
        guild = interaction.guild
        if guild is None:
            return 1
        ac_channels = [
            vc
            for vc in guild.voice_channels
            if str(vc.category).lower().startswith(category.lower())
            and vc.name.startswith(snapshot.custom_prefix)
        ]
        return len(ac_channels) + 1

    async def createVCInvite(
        self, interaction: discord.Interaction, voice_channel: discord.VoiceChannel
    ) -> discord.Invite:
        """Create an invite link for a voice channel.

        Args:
            interaction: The interaction that triggered the command.
            voice_channel: The voice channel to create the invite for.

        Returns:
            An invite for the voice channel.
        """
        return await voice_channel.create_invite()

    def validateCategory(self, interaction: discord.Interaction, category: str) -> bool:
        """Validate if a category exists for the given interaction.

        Args:
            interaction: The interaction that triggered the validation.
            category: The category name to validate.

        Returns:
            True if the category exists, False otherwise.
        """
        server_categories = self.getGuildCategories(interaction)
        LOG.debug(f"Categories found: {server_categories}")
        return any(cat in category.lower() for cat in server_categories)

    def getGuildCategories(self, interaction: discord.Interaction) -> list[str]:
        """Get a list of category names from the guild.

        Args:
            interaction: The interaction context.

        Returns:
            List of lowercase category names.
        """
        guild = interaction.guild
        if guild is None:
            return []
        return [cat.name.lower() for cat in guild.categories]


async def setup(autochannel: AutoChannel) -> None:
    """Setup the AutoChannels extension.

    Args:
        autochannel: The bot instance.
    """
    await autochannel.add_cog(AutoChannels(autochannel))
