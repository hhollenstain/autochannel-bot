import logging
from autochannel.data import db
from autochannel.data.models import Guild, Category, Channel
from autochannel.ui.lib.utils import str2bool

LOG = logging.getLogger(__name__)

def data_update_cat_enable(channel_id, enabled):
    """[summary]
    
    Arguments:
        channel_id {[type]} -- [description]
        enabled {[type]} -- [description]
    """
    enabled = str2bool(enabled)
    category = Category.query.get(channel_id)
    category.enabled = enabled
    db.session.commit()

def data_update_cat_custom_enable(channel_id, enabled):
    """[summary]
    
    Arguments:
        channel_id {[type]} -- [description]
        enabled {[type]} -- [description]
    """
    enabled = str2bool(enabled)
    category = Category.query.get(channel_id)
    category.custom_enabled = enabled
    db.session.commit()

def data_update_cat_prefix(channel_id, prefix):
    """[summary]
    
    Arguments:
        channel_id {[type]} -- [description]
        prefix {[type]} -- [description]
    """
    category = Category.query.get(channel_id)
    category.prefix = prefix
    db.session.commit()

def data_update_cat_custom_prefix(channel_id, prefix):
    """[summary]
    
    Arguments:
        channel_id {[type]} -- [description]
        prefix {[type]} -- [description]
    """
    category = Category.query.get(channel_id)
    category.custom_prefix = prefix
    db.session.commit()

def data_update_cat_channel_size(channel_id, channel_size):
    """[summary]
    
    Arguments:
        channel_id {[type]} -- [description]
        channel_size {[type]} -- [description]
    """
    category = Category.query.get(channel_id)
    category.channel_size = channel_size
    db.session.commit()

def data_update_cat_empty_count(channel_id, empty_count):
    """[summary]
    
    Arguments:
        channel_id {[type]} -- [description]
        channel_size {[type]} -- [description]
    """
    category = Category.query.get(channel_id)
    category.empty_count = empty_count
    db.session.commit()

def data_update_guild_categories(guild_id, categories):
    """[summary]
    
    Arguments:
        guild_id {[type]} -- [description]
        categories {[type]} -- [description]
    """
    cats = list(Category.query.with_entities(Category.id).filter_by(guild_id=guild_id).all())
    cats = [i[0] for i in cats]
    """This converts a list of tuples to a list for my own sanity
    """
    existing_cats = [int(c) for c in categories]
    """Creates a list of existing cats in discord
    """
    miss_cats = set(existing_cats).difference(cats)
    delete_cats = set(cats).difference(existing_cats)

    if len(miss_cats) > 0 or len(delete_cats) > 0:
        update_categories = True
    else:
        update_categories = False

    for mc in miss_cats:
        cat_id_add = Category(id=mc, guild_id=guild_id)
        db.session.add(cat_id_add)
        LOG.debug(f'Adding category: {categories[str(mc)]["name"]} to guild: {guild_id}')        

    for dc in delete_cats: 
        cat_id_delete = Category.query.get(dc)
        for chan in cat_id_delete.get_channels():
            chan_id_delete = Channel.query.get(chan)
            LOG.debug(f'deleting channel due to missing parent category {chan_id_delete}')
            db.session.delete(chan_id_delete)
        db.session.delete(cat_id_delete)
        LOG.debug(f'Deleting category: {dc} that no longer exists in the Guild')

    if update_categories:
        db.session.commit()

def get_guild_from_db(guild_id=None):
    """[summary]
    
    Keyword Arguments:
        guild_id {[type]} -- [description] (default: {None})
    
    Returns:
        [type] -- [description]
    """
    guild = db.session.query(Guild).get(guild_id)
    return guild