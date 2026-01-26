import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
"""AC imports"""
from autochannel.data.models import Guild, Category, Channel

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
    
    def get_category_with_channels(self, session: Session, category_id: int) -> Optional[Category]:
        """Get category with channels eagerly loaded"""
        return (session.query(Category)
                .options(selectinload(Category.channels))
                .get(category_id))
    
    def get_categories_batch(self, session: Session, category_ids: List[int]) -> Dict[int, Category]:
        """Get multiple categories with channels in a single query"""
        categories = (session.query(Category)
                     .options(selectinload(Category.channels))
                     .filter(Category.id.in_(category_ids))
                     .all())
        return {cat.id: cat for cat in categories}
    
    def get_channels_batch(self, session: Session, channel_ids: List[int]) -> Dict[int, Channel]:
        """Get multiple channels in a single query"""
        channels = (session.query(Channel)
                   .filter(Channel.id.in_(channel_ids))
                   .all())
        return {ch.id: ch for ch in channels}
    
    def get_categories_by_guild(self, session: Session, guild_id: int, enabled: Optional[bool] = None) -> List[Category]:
        """Get categories for a guild with optional enabled filter, with channels eagerly loaded"""
        query = (session.query(Category)
                .options(selectinload(Category.channels))
                .filter(Category.guild_id == guild_id))
        if enabled is not None:
            query = query.filter(Category.enabled == enabled)
        return query.all()