"""Pytest configuration and fixtures."""

import pytest
from autochannel.data.models import Guild, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def session():
    """Create an in-memory database session."""
    engine = create_engine("sqlite:///:memory:")
    db.Model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def guild(session):
    """Create a guild fixture."""
    guild = Guild()
    session.add(guild)
    session.commit()
    session.refresh(guild)
    return guild
