"""Browser redirect endpoints for Discord OAuth.

These stay server side (rather than in the SPA) because the OAuth client secret and
session cookie live here. Paths are unchanged so the redirect URIs registered with
Discord keep working.
"""
import logging
from flask import Blueprint, redirect, request, session
from flask import current_app as app
"""App imports"""
from autochannel.api import api_functions
from autochannel.data import data_functions
from autochannel.lib import discordData
from autochannel.lib.auth import is_authenticated, get_managed_guild

LOG = logging.getLogger(__name__)

mod_auth = Blueprint('mod_auth', __name__)


def frontend(path='/'):
    return redirect(f"{app.config['FRONTEND_URL']}{path}")


@mod_auth.route('/login')
def login():
    discord = api_functions.make_session()
    authorization_url, state = discord.authorization_url(app.config['AUTHORIZATION_BASE_URL'])
    session['oauth2_state'] = state
    return redirect(authorization_url)


@mod_auth.route('/logout')
def logout():
    session.clear()
    return frontend('/')


@mod_auth.route('/api/callback')
def callback():
    if request.values.get('error'):
        LOG.info(f"OAuth login failed: {request.values['error']}")
        return frontend('/')

    discord = api_functions.make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        app.config['TOKEN_URL'],
        client_secret=app.config['OAUTH2_CLIENT_SECRET'],
        authorization_response=request.url)

    session.clear()
    session.permanent = True
    session['oauth2_token'] = token
    session['user'] = discordData.parse_user(api_functions.get_user(token))
    session['guilds'] = api_functions.get_managed_guilds(token)
    return frontend('/dashboard')


@mod_auth.route('/api/add-guild', methods=['GET'])
def add_guild():
    """Discord redirects here after the bot is added to a server."""
    if not is_authenticated():
        return redirect('/login')

    guild_id = request.args.get('guild_id', '')
    if not guild_id.isdigit() or get_managed_guild(guild_id) is None:
        return frontend('/dashboard')

    data_functions.add_guild(guild_id)
    return frontend(f'/guild-added/{guild_id}')
