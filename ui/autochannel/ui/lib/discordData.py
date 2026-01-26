import logging
from flask import current_app as app

LOG = logging.getLogger(__name__)

# def discord_parse_data(data, type):
#     return parsed_data

def parse_managed_guilds(data):
    parsed_managed_guilds = {}
    for guild in data:
        parsed_managed_guilds[guild['name']] = {
            'id': guild['id'],
            'name': guild['name'],
            'permissions': guild['permissions'],
        }
        if guild['icon']:
          parsed_managed_guilds[guild['name']]['icon'] = f"{app.config['GUILD_ICON_BASE']}{guild['id']}/{guild['icon']}.jpg"
        else:
          parsed_managed_guilds[guild['name']]['icon'] = app.config['DEFAULT_AVATAR']
    return parsed_managed_guilds

#https://cdn.discordapp.com/icons/{{guilds[server]['id']}}/{{guilds[server]['icon']}}.jpg

def parsed_categories(data):
  """
  """
  parsed_categories = {}
  for category in data:
    parsed_categories[category['id']] = {
      'guild_id': category['guild_id'],
      'name': category['name'],
    }
  return parsed_categories

# def get_guild_icon(icon):


#     return full_icon

"""
{
  "managedGuilds": [
    {
      "icon": "c6c3f81cb6ccb1a392ee07e9c10b8d8f", 
      "id": "321048288574963722", 
      "name": "Planet Express", 
      "owner": true, 
      "permissions": 2147483647
    }, 
    {
      "icon": null, 
      "id": "129238373448679425", 
      "name": "Tamago", 
      "owner": true, 
      "permissions": 2147483647
    }, 
    {
      "icon": "224976a73c4ca7736147d478a84b3eeb", 
      "id": "298160650880942081", 
      "name": "The Salute Down Below", 
      "owner": false, 
      "permissions": 2147483647
    }
  ]
}
"""