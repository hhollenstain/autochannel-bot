from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DB:
    """Database connection manager."""

    def __init__(self) -> None:
        """Initialize the database connection."""
        self.engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URI", ""))
        self._session_factory = sessionmaker(bind=self.engine)

    def session(self) -> Session:
        """Create and return a new database session.

        Returns:
            A new database session.
        """
        return self._session_factory()
