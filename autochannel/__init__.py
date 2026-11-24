from flask import Flask
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
"""AC imports"""
from autochannel.config import Config
from autochannel_db import Base

# Models live in the shared autochannel-db package; Flask-SQLAlchemy only manages
# the engine/session lifecycle against that package's metadata.
db = SQLAlchemy(metadata=Base.metadata)
compress = Compress()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    db.init_app(app)
    compress.init_app(app)
    if not app.testing:
        PrometheusMetrics(app)

    from autochannel.api.routes import mod_api
    from autochannel.auth.routes import mod_auth
    from autochannel.errors.routes import mod_errors
    from autochannel.frontend.routes import mod_frontend

    app.register_blueprint(mod_auth)
    app.register_blueprint(mod_api, url_prefix='/api')
    app.register_blueprint(mod_errors)
    app.register_blueprint(mod_frontend)

    return app
