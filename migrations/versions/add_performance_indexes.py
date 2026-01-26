"""add performance indexes

Revision ID: f1e2d3c4b5a6
Revises: 11b55cea52bb
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1e2d3c4b5a6'
down_revision = '11b55cea52bb'
branch_labels = None
depends_on = None


def upgrade():
    # Index on channel.cat_id for faster category lookups
    op.create_index('idx_channel_cat_id', 'channel', ['cat_id'], unique=False)
    
    # Index on category.guild_id for faster guild lookups
    op.create_index('idx_category_guild_id', 'category', ['guild_id'], unique=False)
    
    # Index on category.enabled for filtering enabled categories
    op.create_index('idx_category_enabled', 'category', ['enabled'], unique=False)
    
    # Index on category.custom_enabled for filtering custom enabled categories
    op.create_index('idx_category_custom_enabled', 'category', ['custom_enabled'], unique=False)
    
    # Composite index for common query pattern: guild_id + enabled
    op.create_index('idx_category_guild_enabled', 'category', ['guild_id', 'enabled'], unique=False)
    
    # Composite index for common query pattern: guild_id + custom_enabled
    op.create_index('idx_category_guild_custom', 'category', ['guild_id', 'custom_enabled'], unique=False)


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('idx_category_guild_custom', table_name='category')
    op.drop_index('idx_category_guild_enabled', table_name='category')
    op.drop_index('idx_category_custom_enabled', table_name='category')
    op.drop_index('idx_category_enabled', table_name='category')
    op.drop_index('idx_category_guild_id', table_name='category')
    op.drop_index('idx_channel_cat_id', table_name='channel')
