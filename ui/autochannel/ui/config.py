import os
from datetime import timedelta

class Config:
    AC_TOKEN = os.getenv('AC_TOKEN')
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
    AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
    AVATAR_BASE_URL = "https://cdn.discordapp.com/avatars/"
    DEFAULT_AVATAR = "https://discordapp.com/assets/"\
                "1cbd08c76f8af6dddce02c5138971129.png"
    GUILD_ICON_BASE = "https://cdn.discordapp.com/icons/"
    OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
    OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
    OAUTH2_REDIRECT_URI = os.environ['OAUTH2_REDIRECT_URI']
    PERMANENT_SESSION_LIFETIME =  timedelta(minutes=60)
    SECRET_KEY = os.environ['OAUTH2_CLIENT_SECRET']
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_URL = API_BASE_URL + '/oauth2/token'
    VERSION_INFO = (0, 0, 1)
    VERSION = '.'.join(str(c) for c in VERSION_INFO)
