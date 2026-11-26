import os
from datetime import timedelta
from pathlib import Path


class Config:
    AC_TOKEN = os.getenv('AC_TOKEN')
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discord.com/api/v10')
    AUTHORIZATION_BASE_URL = 'https://discord.com/oauth2/authorize'
    AVATAR_BASE_URL = 'https://cdn.discordapp.com/avatars/'
    DEFAULT_AVATAR = 'https://cdn.discordapp.com/embed/avatars/0.png'
    GUILD_ICON_BASE = 'https://cdn.discordapp.com/icons/'
    OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
    OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
    OAUTH2_REDIRECT_URI = os.environ['OAUTH2_REDIRECT_URI']
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    SECRET_KEY = os.environ.get('SECRET_KEY') or OAUTH2_CLIENT_SECRET
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    TOKEN_URL = API_BASE_URL + '/oauth2/token'
    # Built React app served by Flask. In local dev the Vite server runs separately,
    # so FRONTEND_URL points OAuth redirects back at it (e.g. http://localhost:5173).
    FRONTEND_DIST = os.environ.get(
        'FRONTEND_DIST', str(Path(__file__).resolve().parent.parent / 'frontend' / 'dist')
    )
    FRONTEND_URL = os.environ.get('FRONTEND_URL', '').rstrip('/')
    VERSION = '3.0.0'
