import pytest

from autochannel_ui import db
from autochannel_ui.api import api_functions
from autochannel_db import Category, Channel, Guild
from conftest import CAT_ID, GUILD_ID, OTHER_GUILD_ID

NEW_CAT_ID = '400000000000000002'


@pytest.fixture
def discord_categories(monkeypatch):
    categories = [
        {'id': NEW_CAT_ID, 'name': 'Squads', 'position': 0},
        {'id': CAT_ID, 'name': 'Raids', 'position': 1},
    ]
    monkeypatch.setattr(api_functions, 'get_guild_categories', lambda gid: categories)
    return categories


def test_me_requires_login(client):
    assert client.get('/api/me').status_code == 401


def test_me(logged_in):
    body = logged_in.get('/api/me').get_json()
    assert body['user']['username'] == 'hank'
    assert body['guilds'][0]['id'] == GUILD_ID


def test_guild_not_managed(logged_in):
    assert logged_in.get(f'/api/guilds/{OTHER_GUILD_ID}').status_code == 404


def test_guild_without_bot_returns_invite(logged_in):
    res = logged_in.get(f'/api/guilds/{GUILD_ID}')
    assert res.status_code == 409
    assert f'guild_id={GUILD_ID}' in res.get_json()['invite_url']


def test_guild_bot_removed_returns_invite(logged_in, guild_with_category, monkeypatch):
    monkeypatch.setattr(api_functions, 'get_guild_categories', lambda gid: None)
    assert logged_in.get(f'/api/guilds/{GUILD_ID}').status_code == 409


def test_guild_syncs_categories(logged_in, guild_with_category, discord_categories, app):
    # A category deleted in Discord is removed (with its channels); new ones are added.
    gone = Category(id=999, guild_id=int(GUILD_ID))
    gone.channels.append(Channel(id=501, num_suffix=1))
    db.session.add(gone)
    db.session.commit()

    body = logged_in.get(f'/api/guilds/{GUILD_ID}').get_json()

    assert body['guild']['name'] == 'Planet Express'
    assert [c['id'] for c in body['categories']] == [NEW_CAT_ID, CAT_ID]
    new = body['categories'][0]
    assert new == {
        'id': NEW_CAT_ID, 'name': 'Squads', 'enabled': False, 'prefix': 'AC!',
        'channel_size': 10, 'empty_count': 1, 'custom_enabled': False, 'custom_prefix': 'VC!',
    }
    assert db.session.get(Category, 999) is None
    assert db.session.get(Channel, 501) is None
    assert db.session.get(Channel, 500) is not None


def test_update_category(logged_in, guild_with_category):
    res = logged_in.patch(
        f'/api/guilds/{GUILD_ID}/categories/{CAT_ID}',
        json={'enabled': True, 'prefix': ' [NA] ', 'channel_size': 0, 'empty_count': 10},
    )
    assert res.status_code == 200
    assert res.get_json()['category']['prefix'] == '[NA]'

    category = db.session.get(Category, int(CAT_ID))
    assert (category.enabled, category.prefix, category.channel_size, category.empty_count) == (
        True, '[NA]', 0, 10
    )


@pytest.mark.parametrize('payload', [
    {'channel_size': 100},
    {'channel_size': -1},
    {'empty_count': 0},
    {'empty_count': True},
    {'enabled': 'true'},
    {'prefix': '   '},
    {'custom_prefix': 'x' * 11},
    {'guild_id': 1},
    {},
])
def test_update_category_validation(logged_in, guild_with_category, payload):
    res = logged_in.patch(f'/api/guilds/{GUILD_ID}/categories/{CAT_ID}', json=payload)
    assert res.status_code == 400
    assert db.session.get(Category, int(CAT_ID)).to_dict()['channel_size'] == 10


def test_update_category_must_belong_to_guild(logged_in, guild_with_category):
    """A user can't edit another server's category by pairing it with a guild they manage."""
    db.session.add_all([Guild(id=int(OTHER_GUILD_ID)), Category(id=7, guild_id=int(OTHER_GUILD_ID))])
    db.session.commit()

    res = logged_in.patch(f'/api/guilds/{GUILD_ID}/categories/7', json={'enabled': True})
    assert res.status_code == 404
    res = logged_in.patch(f'/api/guilds/{OTHER_GUILD_ID}/categories/7', json={'enabled': True})
    assert res.status_code == 404
    assert db.session.get(Category, 7).enabled is False


def test_update_requires_login(client, guild_with_category):
    res = client.patch(f'/api/guilds/{GUILD_ID}/categories/{CAT_ID}', json={'enabled': True})
    assert res.status_code == 401


def test_add_guild(logged_in):
    res = logged_in.get(f'/api/add-guild?guild_id={GUILD_ID}&code=abc')
    assert res.status_code == 302
    assert res.headers['Location'] == f'/guild-added/{GUILD_ID}'
    assert db.session.get(Guild, int(GUILD_ID)) is not None


def test_add_guild_rejects_unmanaged(logged_in):
    res = logged_in.get(f'/api/add-guild?guild_id={OTHER_GUILD_ID}')
    assert res.headers['Location'] == '/dashboard'
    assert db.session.get(Guild, int(OTHER_GUILD_ID)) is None


def test_add_guild_requires_login(client):
    res = client.get(f'/api/add-guild?guild_id={GUILD_ID}')
    assert res.headers['Location'] == '/login'


def test_logout_clears_session(logged_in):
    logged_in.get('/logout')
    assert logged_in.get('/api/me').status_code == 401


def test_unknown_api_route_is_json_404(client):
    res = client.get('/api/nope')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_spa_routes_serve_index(client):
    for path in ('/', '/dashboard', f'/dashboard/1/{GUILD_ID}', '/instructions'):
        res = client.get(path)
        assert res.status_code == 200
        assert b'id="root"' in res.data


def test_spa_serves_assets(client):
    res = client.get('/assets/app-abc123.js')
    assert res.status_code == 200
    assert res.cache_control.max_age == 60 * 60 * 24 * 365
