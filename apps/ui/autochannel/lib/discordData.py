"""Shape Discord API payloads into what the session and frontend need.

Discord ids are snowflakes larger than 2**53, so they are kept as strings for JSON.
"""
from flask import current_app as app

CATEGORY_CHANNEL_TYPE = 4


def parse_managed_guilds(data):
    guilds = []
    for guild in data:
        if guild.get('icon'):
            icon = f"{app.config['GUILD_ICON_BASE']}{guild['id']}/{guild['icon']}.png"
        else:
            icon = app.config['DEFAULT_AVATAR']
        guilds.append({'id': str(guild['id']), 'name': guild['name'], 'icon': icon})
    return sorted(guilds, key=lambda g: g['name'].lower())


def parse_user(user):
    if user.get('avatar'):
        avatar = f"{app.config['AVATAR_BASE_URL']}{user['id']}/{user['avatar']}.png"
    else:
        avatar = app.config['DEFAULT_AVATAR']
    return {
        'id': str(user['id']),
        'username': user.get('global_name') or user['username'],
        'avatar': avatar,
    }


def parse_categories(channels):
    categories = [
        {'id': str(c['id']), 'name': c['name'], 'position': c.get('position', 0)}
        for c in channels
        if c['type'] == CATEGORY_CHANNEL_TYPE
    ]
    return sorted(categories, key=lambda c: c['position'])
