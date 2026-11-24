"""Serve the built React app; React Router handles every non-API path."""
from pathlib import Path

from flask import Blueprint, abort, send_from_directory
from flask import current_app as app
from werkzeug.security import safe_join

mod_frontend = Blueprint('mod_frontend', __name__)

ONE_YEAR = 60 * 60 * 24 * 365


@mod_frontend.route('/', defaults={'path': ''})
@mod_frontend.route('/<path:path>')
def spa(path):
    if path == 'api' or path.startswith('api/'):
        abort(404)

    dist = app.config['FRONTEND_DIST']
    asset = safe_join(dist, path) if path else None
    if asset and Path(asset).is_file():
        # Vite fingerprints everything under assets/, so it can be cached forever.
        max_age = ONE_YEAR if path.startswith('assets/') else None
        return send_from_directory(dist, path, max_age=max_age)

    if not Path(dist, 'index.html').is_file():
        abort(404, description='Frontend not built: run `npm run build` in frontend/')
    response = send_from_directory(dist, 'index.html', max_age=0)
    response.cache_control.no_cache = True
    return response
