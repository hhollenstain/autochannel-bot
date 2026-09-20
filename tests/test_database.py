"""Tests for the data/database module."""

import pytest
import unittest.mock as mock
import os

# We need to set the environment variable for the DB to initialize
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

from autochannel.data.database import DB


class TestDB:
    """Test cases for the DB class."""

    def test_db_init_sets_engine(self):
        """Test that DB initializes the engine."""
        db = DB()
        assert db.engine is not None

    @mock.patch('autochannel.data.database.os.getenv')
    def test_db_init_uses_env_var(self, mock_getenv):
        """Test that DB uses SQLALCHEMY_DATABASE_URI from env."""
        mock_getenv.return_value = 'postgresql://test:pass@localhost/testdb'
        db = DB()
        assert 'postgresql' in str(db.engine.url)

    def test_db_session_returns_session(self):
        """Test that DB.session() returns a session."""
        db = DB()
        session = db.session()
        # Session should be a SQLAlchemy session or similar
        # We can't assert type without full setup, but we can check it's not None
        assert session is not None

    def test_db_session_reusable(self):
        """Test that multiple session calls work."""
        db = DB()
        session1 = db.session()
        session2 = db.session()
        # Sessions may be same or different depending on implementation
        # The important thing is both should be valid
        assert session1 is not None
        assert session2 is not None


class TestDBWithMockedSession:
    """Test cases for DB using mocked SQLAlchemy components."""

    @mock.patch('autochannel.data.database.create_engine')
    @mock.patch('autochannel.data.database.sessionmaker')
    def test_db_session_creation(self, mock_sessionmaker, mock_create_engine):
        """Test that DB creates session using sessionmaker."""
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine
        
        session_factory = mock.MagicMock()
        sessionmaker.return_value = session_factory
        
        mock_session_instance = mock.MagicMock()
        session_factory.return_value = mock_session_instance

        db = DB()
        result = db.session()

        assert result is mock_session_instance
        session_factory.assert_called_once()

    @mock.patch('autochannel.data.database.os.getenv')
    @mock.patch('autochannel.data.database.create_engine')
    def test_db_init_engine_created(self, mock_create_engine, mock_getenv):
        """Test that DB creates engine during init."""
        mock_getenv.return_value = 'sqlite:///memory'
        
        mock_engine = mock.MagicMock()
        mock_create_engine.return_value = mock_engine

        db = DB()

        mock_create_engine.assert_called_once_with('sqlite:///memory')
