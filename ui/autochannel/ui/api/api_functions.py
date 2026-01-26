import os
import logging
import requests
from flask import Flask, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response
from flask import current_app as app
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
from autochannel.ui.lib import discordData

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

def get_guild_categories(server_id):
    """[summary]
    
    Arguments:
        server_id {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    headers = {'Authorization': 'Bot '+app.config['AC_TOKEN']}
    r = requests.get(app.config['API_BASE_URL']+'/guilds/{}/channels'.format(server_id),
                     headers=headers)
    if r.status_code == 200:
        channels = r.json() 
        categories = list(filter(lambda c: c['type'] == 4, channels))
        categories = discordData.parsed_categories(categories)
        return categories
    
    return None

def get_guild_channels(server_id, voice=True, text=True):
    """[summary]
    
    Arguments:
        server_id {[type]} -- [description]
    
    Keyword Arguments:
        voice {bool} -- [description] (default: {True})
        text {bool} -- [description] (default: {True})
    
    Returns:
        [type] -- [description]
    """
    headers = {'Authorization': 'Bot '+app.config['AC_TOKEN']}
    r = requests.get(app.config['API_BASE_URL']+'/guilds/{}/channels'.format(server_id),
                     headers=headers)
    if r.status_code == 200:
        channels = r.json() 
        if not voice:
            channels = list(filter(lambda c: c['type'] != 2, channels))
        if not text:
            channels = list(filter(lambda c: c['type'] != 0, channels))
        return channels
    return None

def get_managed_guilds():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    user = get_user(token)
    guilds = get_user_guilds(token)
    user_servers = sorted(
        get_user_managed_servers(user, guilds),
        key=lambda s: s['name'].lower()
    )
    guild_data = discordData.parse_managed_guilds(user_servers)
    return guild_data

def get_guild(guild_id):
    """[summary]
    
    Arguments:
        guild_id {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    guilds = get_user_guilds(token)
    return list(
        filter( lambda g: (g['id'] in guild_id), guilds)
    )

def get_user(token):
    """[summary]
    
    Arguments:
        token {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    if 'user' in session:
        return session['user']

    discord = make_session(token=token)
    try:
        req = discord.get(app.config['API_BASE_URL'] + '/users/@me')
    except Exception:
        return None

    if req.status_code != 200:
        abort(req.status_code)

    user = req.json()
    # Saving that to the session for easy template access
    session['user'] = user
    return user

def get_user_guilds(token):
    """[summary]
    
    Arguments:
        token {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    # If it's an api_token, go fetch the discord_token
    if token.get('api_key'):
        user_id = token['user_id']
    else:
        user_id = get_user(token)['id']

    discord = make_session(token=token)

    req = discord.get(app.config['API_BASE_URL'] + '/users/@me/guilds')
    if req.status_code != 200:
        abort(req.status_code)

    guilds = req.json()
    return guilds

def get_user_managed_servers(user, guilds):
    """[summary]
    
    Arguments:
        user {[type]} -- [description]
        guilds {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    return list(
        filter(
            lambda g: (g['owner'] is True) or
            bool((int(g['permissions']) >> 5) & 1),
            guilds)
    )

def make_session(token=None, state=None, scope=None):
    """[summary]
    
    Keyword Arguments:
        token {[type]} -- [description] (default: {None})
        state {[type]} -- [description] (default: {None})
        scope {[type]} -- [description] (default: {None})
    
    Returns:
        [type] -- [description]
    """
    scope = ['identify', 'email', 'guilds', 'connections', 'guilds.join']
    return OAuth2Session(
        client_id=app.config['OAUTH2_CLIENT_ID'],
        token=token,
        state=state,
        scope=scope,
        redirect_uri=app.config['OAUTH2_REDIRECT_URI'],
        auto_refresh_kwargs={
            'client_id': app.config['OAUTH2_CLIENT_ID'],
            'client_secret': app.config['OAUTH2_CLIENT_SECRET'],
        },
        auto_refresh_url=app.config['TOKEN_URL'],
        token_updater=token_updater)

def token_updater(token):
    """[summary]
    
    Arguments:
        token {[type]} -- [description]
    """
    session['oauth2_token'] = token