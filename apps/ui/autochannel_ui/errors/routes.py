import logging

from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException

LOG = logging.getLogger(__name__)

mod_errors = Blueprint('mod_errors', __name__)


@mod_errors.app_errorhandler(HTTPException)
def handle_http_error(ex):
    """Every non-SPA route is an API or redirect endpoint, so errors are JSON."""
    return jsonify(error=ex.description), ex.code
