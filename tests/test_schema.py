"""Regression tests that pin the shared database schema.

The schema lives only in the ``autochannel_models`` package. These tests fail if a
table or column is added, removed or renamed, and if the bot stops resolving to the
shared metadata object.
"""

import autochannel_models

EXPECTED_COLUMNS = {
    "guild": {"id"},
    "category": {
        "id",
        "guild_id",
        "enabled",
        "prefix",
        "empty_count",
        "channel_size",
        "custom_enabled",
        "custom_prefix",
    },
    "channel": {"id", "cat_id", "chan_type", "num_suffix"},
}


def test_metadata_has_exactly_the_expected_tables():
    """The shared metadata defines only the guild, category and channel tables."""
    assert set(autochannel_models.Base.metadata.tables) == set(EXPECTED_COLUMNS)


def test_tables_have_exactly_the_expected_columns():
    """Each shared table keeps exactly its current columns."""
    tables = autochannel_models.Base.metadata.tables
    for name, columns in EXPECTED_COLUMNS.items():
        assert set(tables[name].columns.keys()) == columns, name


def test_foreign_keys():
    """Category belongs to a guild and channel belongs to a category."""
    tables = autochannel_models.Base.metadata.tables
    category_fks = {fk.target_fullname for fk in tables["category"].foreign_keys}
    channel_fks = {fk.target_fullname for fk in tables["channel"].foreign_keys}
    assert category_fks == {"guild.id"}
    assert channel_fks == {"category.id"}


def test_bot_uses_shared_metadata():
    """The bot's model module resolves to the shared package objects."""
    from autochannel.data import models as bot_models

    assert bot_models.Base is autochannel_models.Base
    assert bot_models.db is autochannel_models.db
    assert bot_models.db.Model.metadata is autochannel_models.Base.metadata
    for name in ("Guild", "Category", "Channel"):
        assert getattr(bot_models, name) is getattr(autochannel_models, name)
