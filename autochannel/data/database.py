import os
from urllib.parse import urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _database_uri() -> str:
    """Normalize DB URL for SQLAlchemy 2 + psycopg (v3)."""
    raw = os.getenv('SQLALCHEMY_DATABASE_URI') or ''
    if not raw:
        return raw
    if raw.startswith('postgres://'):
        raw = 'postgresql://' + raw[len('postgres://') :]
    parsed = urlparse(raw)
    # Bare ``postgresql://`` defaults to psycopg2 in older stacks; we ship psycopg v3 only.
    if parsed.scheme == 'postgresql':
        parts = list(parsed)
        parts[0] = 'postgresql+psycopg'
        return urlunparse(parts)
    return raw


class DB:
    def __init__(self):
        self.engine = create_engine(_database_uri())
        self._session_factory = sessionmaker(bind=self.engine)

    def session(self):
        return self._session_factory()
