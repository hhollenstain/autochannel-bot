"""JSON API consumed by the React frontend."""
import logging
from flask import Blueprint, jsonify, request, session
"""App imports"""
from autochannel.lib.auth import api_login_required, get_managed_guild
from autochannel.api import api_functions
from autochannel.data import data_functions

LOG = logging.getLogger(__name__)

mod_api = Blueprint('mod_api', __name__)


def _bool(value):
    if not isinstance(value, bool):
        raise ValueError('must be true or false')
    return value


def _int_range(low, high):
    def validate(value):
        if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f'must be a whole number between {low} and {high}')
        return value
    return validate


def _prefix(max_len):
    def validate(value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('can not be empty')
        value = value.strip()
        if len(value) > max_len:
            raise ValueError(f'can be at most {max_len} characters')
        return value
    return validate


# Limits mirror the column sizes in autochannel_db.models and the bot's behaviour.
CATEGORY_FIELDS = {
    'enabled': _bool,
    'prefix': _prefix(100),
    'channel_size': _int_range(0, 99),
    'empty_count': _int_range(1, 10),
    'custom_enabled': _bool,
    'custom_prefix': _prefix(10),
}


def serialize_category(category, name=None):
    data = {'id': str(category.id), **category.to_dict()}
    if name is not None:
        data['name'] = name
    return data


def bot_missing(guild_id):
    return jsonify(
        error='AutoChannel is not in this server',
        invite_url=api_functions.get_invite_link(guild_id),
    ), 409


@mod_api.route('/me')
@api_login_required
def me():
    return jsonify(user=session['user'], guilds=session.get('guilds', []))


@mod_api.route('/guilds/<int:guild_id>')
@api_login_required
def guild_detail(guild_id):
    guild = get_managed_guild(guild_id)
    if guild is None:
        return jsonify(error='Server not found'), 404

    if not data_functions.get_guild_from_db(guild_id):
        return bot_missing(guild_id)

    discord_categories = api_functions.get_guild_categories(guild_id)
    if discord_categories is None:
        # Bot was removed from the guild, so it needs to be re-invited.
        return bot_missing(guild_id)

    db_categories = data_functions.data_update_guild_categories(guild_id, discord_categories)
    categories = [
        serialize_category(db_categories[int(c['id'])], c['name'])
        for c in discord_categories
    ]
    return jsonify(guild=guild, categories=categories)


@mod_api.route('/guilds/<int:guild_id>/categories/<int:category_id>', methods=['PATCH'])
@api_login_required
def update_category(guild_id, category_id):
    if get_managed_guild(guild_id) is None:
        return jsonify(error='Server not found'), 404

    category = data_functions.get_category(guild_id, category_id)
    if category is None:
        return jsonify(error='Category not found'), 404

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not payload:
        return jsonify(error='Expected a JSON object of fields to update'), 400

    updates, errors = {}, {}
    for field, value in payload.items():
        validator = CATEGORY_FIELDS.get(field)
        if validator is None:
            errors[field] = 'unknown field'
            continue
        try:
            updates[field] = validator(value)
        except ValueError as e:
            errors[field] = str(e)
    if errors:
        return jsonify(error='Invalid category settings', fields=errors), 400

    data_functions.update_category(category, **updates)
    LOG.debug(f'Updated category {category_id} in guild {guild_id}: {updates}')
    return jsonify(category=serialize_category(category))
