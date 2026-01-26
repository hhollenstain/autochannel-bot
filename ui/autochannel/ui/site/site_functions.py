import logging
from flask import current_app as app
from flask import session, request

LOG = logging.getLogger(__name__)

def get_invite_link(guild_id):
    """[summary]
    
    Arguments:
        server_id {[type]} -- [description]
    
    Returns:
        [string] -- [string url]
    """
    #permissions = '66321471'
    permissions = '85009'
    domain = request.url_root

    url = f"https://discordapp.com/oauth2/authorize?&client_id={app.config['OAUTH2_CLIENT_ID']}"\
          f"&scope=bot&permissions={permissions}&guild_id={guild_id}&response_type=code"\
          f"&redirect_uri={domain}api/add-guild"     

    return url