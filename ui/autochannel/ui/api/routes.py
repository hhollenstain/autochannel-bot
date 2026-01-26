import os
import logging
import requests
import time
from flask import Flask, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response, Blueprint
from flask import current_app as app
from flask_bootstrap import Bootstrap
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
"""App imports"""
from autochannel.ui.lib.decorators import login_required
from autochannel.ui.lib import discordData
"""Api imports"""
from autochannel.ui.api import api_functions
"""Data Imports"""
from autochannel.ui.data import data_functions
from autochannel.data.models import Guild, Category
from autochannel.data import db

LOG = logging.getLogger(__name__)

mod_api = Blueprint('mod_api', __name__)

@login_required
@mod_api.route('/add-guild', strict_slashes=False, methods=['GET','POST'])
def add_guild():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    guild_id = request.args.get('guild_id')
    guild = api_functions.get_guild(guild_id)
    guild_exists = Guild.query.get(guild_id)
    if not guild_exists:
        guild_id_add = Guild(id=guild_id)
        db.session.add(guild_id_add)
        db.session.commit()
        LOG.debug(f'GUILD Added: {guild_id}')

    return redirect(url_for('mod_site.add_guild', guild_id=guild_id, user_id=session['api_token']['user_id'])) 

@mod_api.route('/callback')
def callback():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    if request.values.get('error'):
        return request.values['error']
    discord = api_functions.make_session(state=session.get('oauth2_state'))
    discord_token = discord.fetch_token(
        app.config['TOKEN_URL'],
        client_secret=app.config['OAUTH2_CLIENT_SECRET'],
        authorization_response=request.url)
    if not discord_token:
        return redirect(url_for('ohno'))

    session['oauth2_token'] = discord_token

    # Fetch the user
    user = api_functions.get_user(discord_token)
    # if not user:
    #     return redirect(url_for('logout'))
    # Generate api_key from user_id
    serializer = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
    api_key = str(serializer.dumps({'user_id': user['id']}))
    # Store api_token in client session
    api_token = {
        'api_key': api_key,
        'user_id': user['id']
    }
    session.permanent = True
    session['api_token'] = api_token
    session['guilds'] = api_functions.get_managed_guilds()
    return redirect(url_for('mod_site.dashboard', user_id=session['api_token']['user_id']))
    
@mod_api.route('/update-enabled-cat',methods=['GET','POST'])
@login_required
def update_enabled_cats():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    enabled = request.form.get('enabled')
    data_functions.data_update_cat_enable(channel_id=channel_id, enabled=enabled)
    msg = 'Updated'
    return jsonify(data=msg)

@mod_api.route('/update-custom-enabled-cat',methods=['GET','POST'])
@login_required
def update_custom_enabled_cats():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    enabled = request.form.get('enabled')
    data_functions.data_update_cat_custom_enable(channel_id=channel_id, enabled=enabled)
    msg = 'Updated'
    return jsonify(data=msg)

@mod_api.route('/update-prefix-cat',methods=['GET','POST'])
@login_required
def update_prefix_cat():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    prefix = request.form.get('prefix')
    data_functions.data_update_cat_prefix(channel_id=channel_id, prefix=prefix)
    msg = f'Updated prefix for channel: {channel_id} to: {prefix} '
    return jsonify(data=msg)

@mod_api.route('/update-custom-prefix-cat',methods=['GET','POST'])
@login_required
def update_custom_prefix_cat():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    prefix = request.form.get('prefix')
    data_functions.data_update_cat_custom_prefix(channel_id=channel_id, prefix=prefix)
    msg = f'Updated prefix for channel: {channel_id} to: {prefix} '
    return jsonify(data=msg)

@mod_api.route('/update-channel_size-cat',methods=['GET','POST'])
@login_required
def update_channel_size_cat():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    channel_size = int(request.form.get('channel_size'))
    if channel_size < 0 or channel_size > 99:
        return jsonify(error='channel size can not be less 0 or greater than 99'), 400
    data_functions.data_update_cat_channel_size(channel_id=channel_id, channel_size=channel_size)
    msg = f'Updated channel size for category: {channel_id} to: {channel_size} '
    return jsonify(data=msg)


@mod_api.route('/update-empty_count-cat',methods=['GET','POST'])
@login_required
def update_empty_count_cat():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    msg=''
    channel_id = request.form.get('channel_id')
    empty_count = int(request.form.get('empty_count'))
    if empty_count < 1 or empty_count > 10:
        return jsonify(error='Empty count can not be less than 1 or greater than 10'), 400
    data_functions.data_update_cat_empty_count(channel_id=channel_id, empty_count=empty_count)
    msg = f'Updated empty channel count for category: {channel_id} to: {empty_count} '
    return jsonify(data=msg)