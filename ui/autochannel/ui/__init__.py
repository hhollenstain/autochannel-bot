import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from prometheus_flask_exporter import PrometheusMetrics
# Import shared db and models from bot
from autochannel.data import db
from autochannel.data.models import Channel, Category, Guild  # noqa: F401
# Import UI-specific config (relative import since config.py is in same directory)
from .config import Config

# UI uses the shared Flask-SQLAlchemy db instance from autochannel.data
# This ensures both bot and UI use the same models and db instance
bcrypt = Bcrypt()
compress = Compress()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize shared db instance with Flask app
    db.init_app(app)
    bcrypt.init_app(app)
    compress.init_app(app)
    PrometheusMetrics(app)

    # Models are already imported from autochannel.data.models above
    # No need to import separately - they use the shared db instance

    # Use relative imports for UI modules
    from .api.routes import mod_api
    from .site.routes import mod_site
    from .errors.routes import mod_errors

    app.register_blueprint(mod_api, url_prefix='/api')
    app.register_blueprint(mod_site)
    app.register_blueprint(mod_errors)

    return app
