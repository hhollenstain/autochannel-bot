"""The shared models and the Alembic history must describe the same schema.

The historical revisions use Postgres-only DDL, so the live comparison needs
TEST_DATABASE_URI pointing at an empty Postgres database (e.g. CI service container).
"""
import io
import os
from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from autochannel_db import Base

ALEMBIC_INI = Path(__file__).parent.parent / 'packages' / 'autochannel-db' / 'alembic.ini'


def alembic_config(url, output_buffer=None):
    cfg = Config(str(ALEMBIC_INI), output_buffer=output_buffer, stdout=io.StringIO())
    cfg.set_main_option('sqlalchemy.url', url)
    return cfg


def test_single_linear_history():
    script = ScriptDirectory.from_config(alembic_config('postgresql://'))
    assert script.get_heads() == ['ac3ce183cdb5']
    assert len(list(script.walk_revisions())) == 9


def test_env_renders_postgres_sql():
    # Offline mode can't render the untyped data UPDATEs in older revisions, so start
    # after the last of them.
    out = io.StringIO()
    command.upgrade(alembic_config('postgresql://', out), 'ad39e8c33891:head', sql=True)
    sql = out.getvalue()
    assert 'CREATE TABLE channel' in sql
    assert "UPDATE alembic_version SET version_num='ac3ce183cdb5'" in sql


@pytest.mark.skipif(not os.environ.get('TEST_DATABASE_URI'), reason='needs Postgres')
def test_migrations_match_models():
    url = os.environ['TEST_DATABASE_URI']
    command.upgrade(alembic_config(url), 'head')

    with create_engine(url).connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []
