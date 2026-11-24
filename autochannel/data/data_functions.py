import logging
from sqlalchemy import select
from autochannel import db
from autochannel_db import Guild, Category

LOG = logging.getLogger(__name__)


def get_guild_from_db(guild_id):
    return db.session.get(Guild, int(guild_id))


def add_guild(guild_id):
    if get_guild_from_db(guild_id):
        return
    db.session.add(Guild(id=int(guild_id)))
    db.session.commit()
    LOG.debug(f'GUILD Added: {guild_id}')


def get_category(guild_id, category_id):
    """Return the category only if it belongs to ``guild_id``."""
    category = db.session.get(Category, int(category_id))
    if category is None or category.guild_id != int(guild_id):
        return None
    return category


def update_category(category, **fields):
    for name, value in fields.items():
        setattr(category, name, value)
    db.session.commit()
    return category


def data_update_guild_categories(guild_id, categories):
    """Make the DB's categories for ``guild_id`` match the ones currently in Discord.

    Arguments:
        guild_id {int|str} -- guild snowflake
        categories {list} -- [{id, name, ...}] from discordData.parse_categories
    """
    guild_id = int(guild_id)
    db_cats = set(db.session.scalars(select(Category.id).filter_by(guild_id=guild_id)))
    discord_cats = {int(c['id']): c['name'] for c in categories}

    miss_cats = discord_cats.keys() - db_cats
    delete_cats = db_cats - discord_cats.keys()

    for mc in miss_cats:
        db.session.add(Category(id=mc, guild_id=guild_id))
        LOG.debug(f'Adding category: {discord_cats[mc]} to guild: {guild_id}')

    for dc in delete_cats:
        # Channel rows go with it via the relationship's delete-orphan cascade.
        db.session.delete(db.session.get(Category, dc))
        LOG.debug(f'Deleting category: {dc} that no longer exists in the Guild')

    if miss_cats or delete_cats:
        db.session.commit()

    return {
        c.id: c
        for c in db.session.scalars(select(Category).filter_by(guild_id=guild_id))
    }
