# Database Migration Consolidation

## Overview

The database migrations have been consolidated from `autochannel-ui` into `autochannel-bot` since both projects share the same database. The bot repository is now the single source of truth for database migrations.

## Changes Made

### 1. Migration Structure ✅
- Copied Alembic configuration (`alembic.ini`) from UI repo
- Created `env.py` adapted for bot's SQLAlchemy setup (not Flask)
- Created migration template (`script.py.mako`)

### 2. Migration Files
**Status:** Migration files need to be copied from UI repo

The following migration files should be copied from `autochannel-ui/migrations/versions/` to `autochannel-bot/migrations/versions/`:

```
cd4835a51fcb_changing_table_name.py
c004761ac578_.py
ad39e8c33891_createing_columns_for_custom_voice_.py
ac3ce183cdb5_adding_suffix_field.py
9aa0046ebc90_.py
760c60b33f07_adding_empty_count_for_category_table.py
69812958030e_changing_primary_key_id.py
5e7904e33be8_creating_channel_table.py
11b55cea52bb_updating_prefix_length.py
```

**Action Required:** Copy these files from the UI repo or they will be synced via git.

### 3. New Migration Created ✅
- `add_performance_indexes.py` - Migration for performance indexes (replaces old SQL file)
  - Revision: `f1e2d3c4b5a6`
  - Revises: `11b55cea52bb` (updating_prefix_length)

### 4. Model Updates ✅
- Updated `Category.prefix` from `String(10)` to `String(100)` to match UI repo
- Model changes now align with both repositories

### 5. Old Files Removed ✅
- Removed `migrations/add_indexes.sql` (replaced with Alembic migration)

## Migration Chain

The complete migration chain should be:

1. `9aa0046ebc90_.py` (or earlier) - Initial schema
2. `ad39e8c33891_createing_columns_for_custom_voice_.py`
3. `5e7904e33be8_creating_channel_table.py`
4. `cd4835a51fcb_changing_table_name.py` - Renamed `channels` to `channel`
5. `ac3ce183cdb5_adding_suffix_field.py`
6. `760c60b33f07_adding_empty_count_for_category_table.py`
7. `69812958030e_changing_primary_key_id.py`
8. `c004761ac578_.py`
9. `11b55cea52bb_updating_prefix_length.py` - Prefix length 10→100
10. `f1e2d3c4b5a6_add_performance_indexes.py` - **NEW** Performance indexes

## Usage

### Running Migrations

From the bot repository:

```bash
# Set database URL
export SQLALCHEMY_DATABASE_URI="postgresql://user:pass@host/db"

# Check current migration status
alembic current

# Upgrade to latest
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"

# Downgrade one revision
alembic downgrade -1
```

### For UI Repository

The UI repository should reference the bot's migrations or keep its own copies synchronized. Since both use the same database:

- **Option 1:** Run migrations only from bot repo (recommended)
- **Option 2:** Keep migrations synchronized between both repos

## Important Notes

1. **Single Source of Truth:** The bot repo (`autochannel-bot/autochannel/data/models.py`) is now the source of truth for the database schema.

2. **Model Synchronization:** Both repos should keep their models synchronized, with the bot repo as the reference.

3. **Migration Safety:** Always backup your database before running migrations.

4. **Indexes:** The new indexes migration (`f1e2d3c4b5a6`) adds performance optimizations and should be applied to existing databases.

## Next Steps

1. **Copy Migration Files:** Copy remaining migration files from UI repo to bot repo
2. **Test Migrations:** Run `alembic current` and `alembic upgrade head` to verify
3. **Update UI Repo:** Consider removing or deprecating migrations from UI repo
4. **Documentation:** Update both repos' README files with migration instructions

## Troubleshooting

If you encounter issues:

1. Check `alembic current` - should show the latest revision
2. Check `alembic history` - shows full migration chain
3. Verify `SQLALCHEMY_DATABASE_URI` is set correctly
4. Ensure all migration files are present in `migrations/versions/`

---

*Last Updated: [Current Date]*
