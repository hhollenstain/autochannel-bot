"""Tests for the AutoChannel class and discord.py integration."""

import os
import pytest
import discord
import discord.ext.commands
import discord.ext.commands.bot
import discord.app_commands
import discord.object
from discord import Intents

# Set up database URL before importing AutoChannel for test modules
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

from autochannel.autochannel import AutoChannel


class TestAutoChannelInit:
    """Test cases for AutoChannel initialization."""

    def test_init_default_values(self):
        """Test AutoChannel initialization with minimal required args."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=[],
            testing_guild_id=None,
        )
        assert autochannel.env == "dev"
        assert autochannel.stats is None
        assert autochannel.testing_guild_id is None
        assert autochannel.initial_extensions == []

    def test_init_custom_values(self):
        """Test AutoChannel initialization with custom parameters."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=["test_ext"],
            testing_guild_id=123456789,
            app_id="test_app_id",
            auto_channel_prefix="!ac ",
            auto_categories=["auto-voice"],
            env="prod",
            dbl_token="test_token",
            voice_channel_prefix="!vc ",
        )
        assert autochannel.app_id == "test_app_id"
        assert autochannel.auto_channel_prefix == "!ac "
        assert autochannel.auto_categories == ["auto-voice"]
        assert autochannel.env == "prod"
        assert autochannel.dbl_token == "test_token"
        assert autochannel.voice_channel_prefix == "!vc "
        assert autochannel.testing_guild_id == 123456789
        assert autochannel.initial_extensions == ["test_ext"]

    def test_init_testing_guild_id_as_zero(self):
        """Test that testing_guild_id=0 is properly handled (falsy but valid)."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=[],
            testing_guild_id=0,
        )
        assert autochannel.testing_guild_id is None

    def test_init_testing_guild_id_as_none_explicit(self):
        """Test that testing_guild_id=None is properly handled."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=[],
            testing_guild_id=None,
        )
        assert autochannel.testing_guild_id is None


class TestAutoChannelTreeSync:
    """Test cases for tree sync functionality."""

    @pytest.mark.asyncio
    async def test_sync_setup_without_testing_guild(self):
        """Test setup_hook syncs globally when no testing_guild_id."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=[],
            testing_guild_id=None,
        )

        # Track the method calls
        sync_called = []
        original_sync = autochannel.tree.sync
        
        async def mock_sync(*args, **kwargs):
            sync_called.append((args, kwargs))
            return original_sync

        autochannel.tree.sync = mock_sync

        await autochannel.setup_hook()

        # Should have sync called without guild parameter
        assert len(sync_called) == 1
        assert sync_called[0][1].get('guild') is None

    @pytest.mark.asyncio
    async def test_sync_setup_with_testing_guild(self):
        """Test setup_hook copies and syncs to testing guild when testing_guild_id is set."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=[],
            testing_guild_id=987654321,
        )

        # Track method calls
        copy_called = []
        sync_called = []
        original_copy = autochannel.tree.copy_global_to
        original_sync = autochannel.tree.sync
        
        async def mock_copy(*args, **kwargs):
            copy_called.append((args, kwargs))
            return original_copy

        async def mock_sync(*args, **kwargs):
            sync_called.append((args, kwargs))
            return original_sync

        autochannel.tree.copy_global_to = mock_copy
        autochannel.tree.sync = mock_sync

        await autochannel.setup_hook()

        # Should copy global commands to guild and sync
        assert len(copy_called) == 1
        assert copy_called[0][1].get('guild').id == 987654321
        assert len(sync_called) == 1
        assert sync_called[0][1].get('guild').id == 987654321


class TestAutoChannelExtensions:
    """Test extension loading functionality."""

    @pytest.mark.asyncio
    async def test_setup_hook_loads_extensions(self):
        """Test that setup_hook loads the specified extensions."""
        autochannel = AutoChannel(
            command_prefix="!",
            intents=Intents.default(),
            initial_extensions=["test_ext_1", "test_ext_2"],
            testing_guild_id=None,
        )

        # Track load_extension calls
        extensions_loaded = []
        original_load = autochannel.load_extension
        
        def mock_load(extension_name):
            extensions_loaded.append(extension_name)
            return original_load(extension_name)
        
        autochannel.load_extension = mock_load

        await autochannel.setup_hook()

        assert "test_ext_1" in extensions_loaded
        assert "test_ext_2" in extensions_loaded
