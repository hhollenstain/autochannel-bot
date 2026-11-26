import logging
import requests
from flask import session, request, abort
from flask import current_app as app
from requests_oauthlib import OAuth2Session
from autochannel.lib import discordData

"""
Channel types:
0 = text
1 = dm channel
2 = voice
3 = group DM
4 = category
5 = news
6 = store
"""

LOG = logging.getLogger(__name__)

OAUTH2_SCOPE = ['identify', 'email', 'guilds', 'connections', 'guilds.join']
# MANAGE_CHANNELS | VIEW_CHANNEL | CONNECT | MOVE_MEMBERS (unchanged from the jinja UI)
BOT_PERMISSIONS = '85009'
MANAGE_GUILD = 1 << 5


def get_guild_categories(guild_id):
    """Fetch a guild's categories with the bot token.

    Returns:
        list of {id, name, position}, or None when the bot can't see the guild
        (it was never added or has been removed).
    """
    headers = {'Authorization': 'Bot ' + app.config['AC_TOKEN']}
    r = requests.get(f"{app.config['API_BASE_URL']}/guilds/{guild_id}/channels",
                     headers=headers, timeout=10)
    if r.status_code == 200:
        return discordData.parse_categories(r.json())

    LOG.info(f'Bot could not list channels for guild {guild_id}: {r.status_code}')
    return None


def get_user(token):
    discord = make_session(token=token)
    req = discord.get(app.config['API_BASE_URL'] + '/users/@me')
    if req.status_code != 200:
        abort(req.status_code)
    return req.json()


def get_user_guilds(token):
    discord = make_session(token=token)
    req = discord.get(app.config['API_BASE_URL'] + '/users/@me/guilds')
    if req.status_code != 200:
        abort(req.status_code)
    return req.json()


def get_user_managed_servers(guilds):
    """Guilds the user owns or has the Manage Server permission in."""
    return [
        g for g in guilds
        if g.get('owner') is True or bool(int(g['permissions']) & MANAGE_GUILD)
    ]


def get_managed_guilds(token):
    return discordData.parse_managed_guilds(get_user_managed_servers(get_user_guilds(token)))


def get_invite_link(guild_id):
    """URL that adds the bot to ``guild_id`` and returns to /api/add-guild."""
    return (
        f"{app.config['AUTHORIZATION_BASE_URL']}?client_id={app.config['OAUTH2_CLIENT_ID']}"
        f"&scope=bot&permissions={BOT_PERMISSIONS}&guild_id={guild_id}"
        f"&disable_guild_select=true&response_type=code"
        f"&redirect_uri={request.url_root}api/add-guild"
    )


def make_session(token=None, state=None):
    return OAuth2Session(
        client_id=app.config['OAUTH2_CLIENT_ID'],
        token=token,
        state=state,
        scope=OAUTH2_SCOPE,
        redirect_uri=app.config['OAUTH2_REDIRECT_URI'],
        auto_refresh_kwargs={
            'client_id': app.config['OAUTH2_CLIENT_ID'],
            'client_secret': app.config['OAUTH2_CLIENT_SECRET'],
        },
        auto_refresh_url=app.config['TOKEN_URL'],
        token_updater=token_updater)


def token_updater(token):
    session['oauth2_token'] = token
