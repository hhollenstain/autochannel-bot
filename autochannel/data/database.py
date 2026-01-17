import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
"""AC imports"""
from autochannel.data.models import Guild, Category

LOG = logging.getLogger(__name__)

class DB:
    def __init__(self):
        database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        # Add connection pooling settings for better reliability
        self.engine = create_engine(
            database_uri,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            pool_size=5,          # Maintain 5 connections in pool
            max_overflow=10,     # Allow up to 10 overflow connections
            echo=False
        )
        self.Session = sessionmaker(bind=self.engine)

    def session(self):
        """Create a new database session"""
        session = self.Session()
        # Ensure session is in a clean state
        try:
            # Rollback any pending transaction
            if session.in_transaction():
                session.rollback()
        except Exception:
            # If rollback fails, close and create new session
            session.close()
            session = self.Session()
        return session
    
    @contextmanager
    def safe_session(self):
        """Context manager for safe database operations with automatic rollback"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            LOG.error(f"Database error, rolled back transaction: {e}")
            raise
        finally:
            session.close()
