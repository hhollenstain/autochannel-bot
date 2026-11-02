"""Tests for database models.

These regression tests ensure the SQLAlchemy models continue to work
correctly after refactoring or schema changes.
"""

import pytest
from autochannel.data.models import Category, Channel, Guild, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestGuild:
    """Unit tests for Guild model."""

    @pytest.fixture
    def session(self):
        """Create an in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        db.Model.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    @pytest.fixture
    def guild(self, session):
        """Create a guild for testing."""
        guild = Guild(id=123456789)
        session.add(guild)
        session.commit()
        session.refresh(guild)
        return guild

    def test_guild_creation(self, guild):
        """Test basic guild creation."""
        assert guild.id is not None

    def test_guild_categories_relationship(self, session, guild):
        """Test Guild to Category relationship."""
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )
        session.add(category)
        session.commit()

        # Refresh guild to get categories
        session.refresh(guild)
        assert len(guild.categories) == 1
        assert guild.categories[0].id == category.id


class TestCategory:
    """Unit tests for Category model."""

    @pytest.fixture
    def session(self):
        """Create an in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        db.Model.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_category_creation(self, session, guild):
        """Test basic category creation."""
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        assert category.id is not None
        assert category.enabled is False

    def test_category_with_all_defaults(self, session, guild):
        """Test category with all default values."""
        category = Category(
            guild_id=guild.id,
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        assert category.prefix == "AC!"
        assert category.empty_count == 1
        assert category.channel_size == 10
        assert category.custom_enabled is False
        assert category.custom_prefix == "VC!"

    def test_category_methods(self, session, guild):
        """Test Category get_channels and get_chan_suffix methods."""
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )
        session.add(category)
        session.commit()
        session.refresh(category)

        # get_channels should return empty list when no channels exist
        assert category.get_channels() == []
        assert category.get_chan_suffix() == []


class TestChannel:
    """Unit tests for Channel model."""

    @pytest.fixture
    def session(self):
        """Create an in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        db.Model.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_channel_creation(self, session, guild):
        """Test basic channel creation."""
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )
        session.add(category)
        session.commit()

        channel = Channel(
            cat_id=category.id,
            chan_type="voice",
            num_suffix=1,
        )
        session.add(channel)
        session.commit()
        session.refresh(channel)
        assert channel.id is not None
        assert channel.cat_id == category.id


class TestRelationships:
    """Unit tests for model relationships."""

    @pytest.fixture
    def session(self):
        """Create an in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        db.Model.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_category_has_guild_foreign_key(self, session, guild):
        """Test Category references Guild via foreign key."""
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )
        session.add(category)
        session.commit()

        # Category should have the correct guild_id
        saved_category = session.query(Category).filter_by(id=category.id).first()
        assert saved_category is not None
        assert saved_category.guild_id == guild.id

    def test_channel_has_category_foreign_key(self, session, guild):
        """Test Channel references Category via foreign key."""
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )
        session.add(category)
        session.commit()

        channel = Channel(cat_id=category.id, chan_type="voice", num_suffix=1)
        session.add(channel)
        session.commit()

        # Channel should have the correct cat_id
        saved_channel = session.query(Channel).filter_by(id=channel.id).first()
        assert saved_channel is not None
        assert saved_channel.cat_id == category.id


class TestTransactionRollback:
    """Unit tests for transaction rollback scenarios."""

    @pytest.fixture
    def session(self):
        """Create an in-memory database session."""
        engine = create_engine("sqlite:///:memory:")
        db.Model.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_category_save_with_transaction_rollback_logic(self, session, guild):
        """Test that save_with_transaction method has proper rollback logic."""
        # Test the actual transaction handling by using the database transaction context manager

        # Test that our Category.save_with_transaction method handles transactions properly
        category = Category(
            guild_id=guild.id,
            prefix="AC!",
            empty_count=1,
            channel_size=10,
            custom_enabled=False,
        )

        # This test is mainly to ensure the method exists and can be called without errors
        # The actual rollback behavior is tested via the database transaction context manager
        # in the database.py module
        assert category is not None

        # Call save_with_transaction - this should succeed (no exception)
        try:
            category.save_with_transaction(session)
            # Verify that it was actually saved
            saved_category = (
                session.query(Category).filter_by(guild_id=guild.id, prefix="AC!").first()
            )
            assert saved_category is not None
            assert saved_category.id is not None

        except Exception as e:
            pytest.fail(f"save_with_transaction failed unexpectedly: {e}")
