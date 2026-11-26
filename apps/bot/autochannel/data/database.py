"""Database engine and session management."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DB:
    """Database connection manager."""

    def __init__(self) -> None:
        """Initialize the database connection."""
        self.engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI", ""), pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self.engine)

    def session(self) -> Session:
        """Create and return a new database session.

        Returns:
            A new database session.
        """
        return self._session_factory()

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        """Provide a transaction context manager for database operations.

        This ensures that database operations are properly committed or rolled back
        in case of exceptions, and that sessions are properly closed. Objects loaded
        in the session expire when it closes, so copy what you need before leaving
        the ``with`` block.

        Yields:
            A session that is committed on success and rolled back on error.
        """
        session = self.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close_all_sessions(self) -> None:
        """Close all database connections in the connection pool."""
        if self.engine is not None:
            self.engine.dispose()
