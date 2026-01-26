# Database Migrations

This directory contains Alembic migrations for the shared AutoChannel database used by both `autochannel-bot` and `autochannel-ui`.

## Structure

- `alembic.ini` - Alembic configuration file
- `env.py` - Alembic environment setup (adapted for bot's SQLAlchemy)
- `versions/` - Migration files (chronological order)

## Migration History

All migrations are shared between both repositories. The bot and UI use the same database schema.

### Current Migrations

1. Initial table creation and schema setup
2. Channel table creation (renamed from `channels` to `channel`)
3. Custom voice channel columns
4. Suffix field addition
5. Empty count for category table
6. Prefix length update (10 → 100 characters)
7. **Performance indexes** - Added indexes for query optimization

## Usage

### Running Migrations (Bot)

```bash
# Set database URL
export SQLALCHEMY_DATABASE_URI="postgresql://user:pass@host/db"

# Check current revision
alembic current

# Upgrade to latest
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"

# Downgrade one revision
alembic downgrade -1
```

### Running Migrations (UI)

The UI repository has its own migrations directory that should be kept in sync. However, since both use the same database, migrations should only be run from one location (preferably the bot repo).

### Creating New Migrations

1. Make changes to `autochannel/data/models.py` in the bot repo
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review the generated migration file
4. Test the migration: `alembic upgrade head`
5. Copy the migration to UI repo if needed for reference

## Notes

- **Always backup your database before running migrations**
- Migrations are shared - changes affect both bot and UI
- The bot's models define the source of truth for the schema
- Indexes and optimizations are tracked in migrations

## Shared Models

Both repositories should keep their models synchronized. The bot repo (`autochannel-bot/autochannel/data/models.py`) is considered the source of truth.
