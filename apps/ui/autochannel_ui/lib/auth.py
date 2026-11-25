import logging
from functools import wraps
from flask import session, jsonify

LOG = logging.getLogger(__name__)


def is_authenticated():
    return bool(session.get('oauth2_token') and session.get('user'))


def api_login_required(view):
    """Reject unauthenticated API calls with 401 so the SPA can send users to /login."""
    @wraps(view)
    def view_wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify(error='Not logged in'), 401
        return view(*args, **kwargs)
    return view_wrapper


def get_managed_guild(guild_id):
    """Return the session's guild entry if the user manages ``guild_id``, else None."""
    gid = str(guild_id)
    return next((g for g in session.get('guilds', []) if g['id'] == gid), None)
