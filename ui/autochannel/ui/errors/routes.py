import logging
from flask import Blueprint, render_template

LOG = logging.getLogger(__name__)

mod_errors = Blueprint('mod_errors', __name__)

@mod_errors.route('/404')
def ac_404():
    return render_template('pages/404.html'), 404

@mod_errors.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('pages/404.html'), 404

@mod_errors.route('/<path:path>')
def catch_all(path):
    return render_template('pages/404.html'), 404

@mod_errors.errorhandler(404)
@mod_errors.errorhandler(405)
def _handle_api_error(ex):
    if request.path.startswith('/api/'):
        return jsonify_error(ex)
    else:
        return ex