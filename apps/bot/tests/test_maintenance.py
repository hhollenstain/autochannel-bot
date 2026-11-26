"""Regression tests for the auto channel maintenance planning rules."""

from autochannel.lib.maintenance import (
    CategorySnapshot,
    channels_to_create,
    channels_to_delete,
    next_suffixes,
)
from autochannel_db import Category, Channel


def _snapshot(**overrides):
    """Build a CategorySnapshot with sensible defaults."""
    values = {
        "id": 10,
        "guild_id": 1,
        "enabled": True,
        "prefix": "AC!",
        "empty_count": 1,
        "channel_size": 10,
        "custom_enabled": False,
        "custom_prefix": "VC!",
        "channels": {},
    }
    values.update(overrides)
    return CategorySnapshot(**values)


def test_next_suffixes_fills_gaps_first():
    """New channels reuse the lowest free numbers."""
    assert next_suffixes([1, 2, 4], 3) == [3, 5, 6]


def test_next_suffixes_none_needed():
    """Asking for zero suffixes returns an empty list."""
    assert next_suffixes([1, 2], 0) == []


def test_channels_to_create():
    """Only create channels up to the target and never a negative amount."""
    assert channels_to_create(0, 2) == 2
    assert channels_to_create(1, 1) == 0
    assert channels_to_create(3, 1) == 0


def test_channels_to_delete_highest_suffix_first():
    """Surplus empty channels are removed starting with the highest number."""
    suffixes = {100: 1, 200: 3, 300: 2}
    assert channels_to_delete([100, 200, 300], suffixes, target=1) == [200, 300]


def test_channels_to_delete_respects_empty_count_zero():
    """A single empty channel is removed when empty_count is 0 (old code kept it)."""
    assert channels_to_delete([100], {100: 1}, target=0) == [100]


def test_channels_to_delete_counts_pending_channels():
    """Channels created but not yet cached count toward the empty total."""
    assert channels_to_delete([100], {100: 1}, target=1, pending=1) == [100]
    assert channels_to_delete([], {}, target=1, pending=1) == []


def test_snapshot_target_empty_when_disabled():
    """Disabled categories want no empty auto channels."""
    assert _snapshot(enabled=False, empty_count=3).target_empty == 0
    assert _snapshot(enabled=True, empty_count=3).target_empty == 3


def test_snapshot_channel_name():
    """Auto channels are named '<prefix> - <suffix>'."""
    assert _snapshot(prefix="Game").channel_name(4) == "Game - 4"


def test_snapshot_from_model_is_detached(session, guild):
    """Snapshots stay usable after the session that loaded them is closed."""
    category = Category(id=10, guild_id=guild.id, enabled=True, prefix="AC!", empty_count=2)
    session.add(category)
    session.add(Channel(id=55, cat_id=10, chan_type="voice", num_suffix=1))
    session.commit()

    snapshot = CategorySnapshot.from_model(session.get(Category, 10))
    session.close()

    assert snapshot.channels == {55: 1}
    assert snapshot.empty_count == 2
    assert snapshot.target_empty == 2
