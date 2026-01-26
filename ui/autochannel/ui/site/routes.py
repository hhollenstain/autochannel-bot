import os
import logging
import requests
import time
from flask import Flask, Blueprint, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response
from flask import current_app as app
from flask_bootstrap import Bootstrap
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
"""AC Imports"""
from autochannel.data import db
from autochannel.data.models import Guild, Category
from autochannel.ui.lib.decorators import login_required, guild_check, guild_owner_check
from autochannel.ui.lib import discordData
from autochannel.ui.api import api_functions
from autochannel.ui.data import data_functions, data_forms
from autochannel.ui.site import site_functions


LOG = logging.getLogger(__name__)

mod_site = Blueprint('mod_site', __name__)

@mod_site.route('/', strict_slashes=False)
def index():
    title = 'Welcome to Autochannel Bot!'
    return render_template('pages/index.html', title=title)

@mod_site.route('/instructions', strict_slashes=False)
def instructions():
    title = 'Instructions to use Auto-chan'
    return render_template('pages/instructions.html', title=title)

def token_updater(token):
    session['oauth2_token'] = token

@login_required
@mod_site.route('/dashboard',  strict_slashes=False)
def dashboard_index():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    if 'oauth2_token' in session:
        return redirect(url_for('mod_site.dashboard', user_id=session['api_token']['user_id']))
    
    return redirect(url_for('mod_site.login')) 

@login_required
@mod_site.route('/guild-added/<user_id>/<guild_id>')
def add_guild(user_id=None, guild_id=None):
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    time.sleep(2)
    guild = api_functions.get_guild(guild_id)
    guild_data = discordData.parse_managed_guilds(guild)
    return render_template('pages/guild-add.html', guild_id=guild_id, guild=guild_data, user_id=user_id)


@mod_site.route('/dashboard/<user_id>')
@login_required
def dashboard(user_id):
    """[summary]
    
    Arguments:
        user_id {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    guilds = session['guilds']
    title = f"Guilds managed by {session['user']['username']}"
    return render_template(
            'pages/selectserver-boot.html', title=title,
            guilds=guilds, user_id=user_id
        )

@mod_site.route('/dashboard/<user_id>/<guild_id>')
@login_required
@guild_owner_check
@guild_check
def dashboard_guild(user_id=None, guild_id=None):
    """[summary]
    
    Keyword Arguments:
        user_id {[type]} -- [description] (default: {None})
        guild_id {[type]} -- [description] (default: {None})
    
    Returns:
        [type] -- [description]
    """
    #channels = api_functions.get_guild_channels(guild_id)
    discord_categories = api_functions.get_guild_categories(guild_id)
    if discord_categories:
        data_functions.data_update_guild_categories(categories=discord_categories, guild_id=guild_id)
        db_categories = Guild.query.get(guild_id).get_categories()
        guild = api_functions.get_guild(guild_id)
        guild_data = discordData.parse_managed_guilds(guild)
        title = "Guild Categories"
    
        return render_template(
                'pages/guild-categories.html', title=title, 
                db_categories=db_categories, discord_categories=discord_categories, 
                guild=guild_data
            )
    else:
        """Bot was removed from guild so re-invite"""
        invite_url = site_functions.get_invite_link(guild_id)
        return redirect(invite_url)

@mod_site.route('/me')
@login_required
def me():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    discord = api_functions.make_session(token=session.get('oauth2_token'))
    user = discord.get(app.config['API_BASE_URL'] + '/users/@me').json()
    guilds = discord.get(app.config['API_BASE_URL'] + '/users/@me/guilds').json()
    connections = discord.get(app.config['API_BASE_URL'] + '/users/@me/connections').json()
    return jsonify(user=user, guilds=guilds, connections=connections)

@mod_site.route('/whoami')
@login_required
def whoami():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    return jsonify(user=api_functions.get_user(token))

@mod_site.route('/api/user')
@login_required
def user():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    token = session['oauth2_token']
    #user_info = get_user(token)
    return jsonify(user=api_functions.get_user(token))

@mod_site.route('/login')
def login():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    scope = ['identify', 'email', 'guilds', 'connections', 'guilds.join']
    discord = api_functions.make_session(scope=scope)
    authorization_url, state = discord.authorization_url(
        app.config['AUTHORIZATION_BASE_URL'],
    )
    session['oauth2_state'] = state
    return redirect(authorization_url) 

@mod_site.route('/logout')
def logout():
    """[summary]

    Returns:
        [type] -- [description]
    """
    session.clear()
    return redirect(url_for('mod_site.index'))

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     if app.debug:
#         return requests.get('http://localhost:8080/{}'.format(path)).text
#     return render_template("index.html")