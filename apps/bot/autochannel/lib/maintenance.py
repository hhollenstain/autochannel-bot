"""Pure planning helpers for auto voice channel maintenance.

These functions hold no Discord or database state so the channel maintenance
rules can be reasoned about (and tested) in isolation from the cog that applies
them.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from autochannel_db import Category


@dataclass(frozen=True, slots=True)
class CategorySnapshot:
    """Detached, read-only copy of a category's configuration and tracked channels.

    ORM objects expire once their session closes, so the cog works from this
    snapshot instead of passing live models between coroutines.

    Attributes:
        id: Discord category ID.
        guild_id: Discord guild ID the category belongs to.
        enabled: Whether auto channels are managed for this category.
        prefix: Name prefix for auto channels.
        empty_count: Number of empty auto channels to keep available.
        channel_size: User limit applied to new auto channels.
        custom_enabled: Whether custom ``/vc`` channels are allowed.
        custom_prefix: Name prefix for custom ``/vc`` channels.
        channels: Mapping of tracked auto channel ID to its numeric suffix.
    """

    id: int
    guild_id: int
    enabled: bool
    prefix: str
    empty_count: int
    channel_size: int
    custom_enabled: bool
    custom_prefix: str
    channels: Mapping[int, int] = field(default_factory=dict)

    @classmethod
    def from_model(cls, category: Category) -> CategorySnapshot:
        """Build a snapshot from a category model while its session is open.

        Args:
            category: The attached category model.

        Returns:
            A snapshot that is safe to use after the session closes.
        """
        return cls(
            id=category.id,
            guild_id=category.guild_id,
            enabled=category.enabled,
            prefix=category.prefix,
            empty_count=category.empty_count,
            channel_size=category.channel_size,
            custom_enabled=category.custom_enabled,
            custom_prefix=category.custom_prefix,
            channels={channel.id: channel.num_suffix for channel in category.channels},
        )

    @property
    def target_empty(self) -> int:
        """Number of empty auto channels this category should have right now."""
        return max(self.empty_count, 0) if self.enabled else 0

    def channel_name(self, suffix: int) -> str:
        """Return the canonical auto channel name for a suffix.

        Args:
            suffix: The channel's numeric suffix.

        Returns:
            The channel name, e.g. ``"AC! - 3"``.
        """
        return f"{self.prefix} - {suffix}"


def next_suffixes(existing: Iterable[int], count: int) -> list[int]:
    """Return the ``count`` lowest positive suffixes not already in use.

    Args:
        existing: Suffixes currently assigned to tracked channels.
        count: How many new suffixes are needed.

    Returns:
        Sorted list of unused suffixes, filling gaps first.
    """
    used = set(existing)
    suffixes: list[int] = []
    candidate = 1
    while len(suffixes) < count:
        if candidate not in used:
            suffixes.append(candidate)
        candidate += 1
    return suffixes


def channels_to_create(empty_count: int, target: int) -> int:
    """Return how many auto channels must be created to reach the target.

    Args:
        empty_count: Empty auto channels that currently exist (or are pending).
        target: Desired number of empty auto channels.

    Returns:
        Number of channels to create (never negative).
    """
    return max(target - empty_count, 0)


def channels_to_delete(
    empty_ids: Sequence[int],
    suffixes: Mapping[int, int],
    target: int,
    pending: int = 0,
) -> list[int]:
    """Pick which empty auto channels to delete, highest suffix first.

    Args:
        empty_ids: IDs of empty auto channels that can be deleted.
        suffixes: Mapping of tracked channel ID to numeric suffix.
        target: Desired number of empty auto channels.
        pending: Empty channels that exist but cannot be deleted yet
            (created but not yet visible in the gateway cache).

    Returns:
        Channel IDs to delete, ordered from highest suffix to lowest.
    """
    surplus = len(empty_ids) + pending - target
    if surplus <= 0:
        return []
    ordered = sorted(empty_ids, key=lambda cid: suffixes.get(cid, 0), reverse=True)
    return ordered[:surplus]
