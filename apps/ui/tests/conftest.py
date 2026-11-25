import os

# Config reads these at import time.
os.environ.setdefault('OAUTH2_CLIENT_ID', 'client-id')
os.environ.setdefault('OAUTH2_CLIENT_SECRET', 'client-secret')
os.environ.setdefault('OAUTH2_REDIRECT_URI', 'http://localhost/api/callback')
os.environ.setdefault('AC_TOKEN', 'bot-token')

import pytest

from autochannel_ui import create_app, db
from autochannel_ui.config import Config
from autochannel_db import Category, Channel, Guild

GUILD_ID = '321048288574963722'
OTHER_GUILD_ID = '129238373448679425'
CAT_ID = '400000000000000001'


@pytest.fixture
def app(tmp_path):
    (tmp_path / 'index.html').write_text('<div id="root"></div>')
    (tmp_path / 'assets').mkdir()
    (tmp_path / 'assets' / 'app-abc123.js').write_text('console.log(1)')

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite://'
        FRONTEND_DIST = str(tmp_path)

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in(client):
    with client.session_transaction() as sess:
        sess['oauth2_token'] = {'access_token': 'x', 'token_type': 'Bearer'}
        sess['user'] = {'id': '1', 'username': 'hank', 'avatar': 'a.png'}
        sess['guilds'] = [{'id': GUILD_ID, 'name': 'Planet Express', 'icon': 'i.png'}]
    return client


@pytest.fixture
def guild_with_category(app):
    guild = Guild(id=int(GUILD_ID))
    category = Category(id=int(CAT_ID), guild_id=int(GUILD_ID))
    category.channels.append(Channel(id=500, chan_type='voice', num_suffix=1))
    db.session.add_all([guild, category])
    db.session.commit()
    return guild
