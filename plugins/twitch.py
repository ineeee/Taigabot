# twitch plugin by ine (2022)
from util import hook
from json import loads as json_load
from utilities import request
import re


TWITCH_RE = (r'https?://(www\.)?twitch.tv/([a-zA-Z0-9_]+)', re.I)
# the token gets renewed automatically when it expires
TWITCH_CURRENT_TOKEN = 'ahahah how is cyber bullying real'
# these get loaded from the bot config
TWITCH_CLIENT_ID = 'taiga rules'
TWITCH_CLIENT_SECRET = 'hunter2'


# get a twitch oauth2 access token
# https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#client-credentials-grant-flow
def twitch_auth():
    data = {
        'client_id': TWITCH_CLIENT_ID,
        'client_secret': TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }

    req = request.post('https://id.twitch.tv/oauth2/token', data=data)
    json = json_load(req)

    if 'access_token' in json:
        return json['access_token']

    return None


def twitch_user_info(user: str):
    user = request.urlencode(user)
    api_bearer = 'Bearer ' + TWITCH_CURRENT_TOKEN
    headers = {'Accept': 'application/json', 'Authorization': api_bearer, 'Client-Id': TWITCH_CLIENT_ID}
    data = request.get_json('https://api.twitch.tv/helix/users?login=' + user, headers=headers)

    return data


def twitch_chan_info(id: int):
    api_bearer = 'Bearer ' + TWITCH_CURRENT_TOKEN
    headers = {'Accept': 'application/json', 'Authorization': api_bearer, 'Client-Id': TWITCH_CLIENT_ID}
    data = request.get_json('https://api.twitch.tv/helix/channels?broadcaster_id=' + id, headers=headers)

    return data


@hook.command
def twitch(inp, bot=None, reply=None):
    """twitch <username> -- gets user and channel info about a twitch.tv streamer"""
    global TWITCH_CURRENT_TOKEN
    global TWITCH_CLIENT_ID
    global TWITCH_CLIENT_SECRET

    TWITCH_CLIENT_ID = bot.config['api_keys'].get('twitch_client_id', None)
    TWITCH_CLIENT_SECRET = bot.config['api_keys'].get('twitch_client_secret', None)

    # first check if our api key still works
    # access tokens expire every few hours
    data_check = twitch_user_info('pokimane')
    if 'error' in data_check:
        if data_check['status'] == 401 and data_check['error'] == 'Unauthorized':
            # access denied, try to reauthenticate
            TWITCH_CURRENT_TOKEN = twitch_auth()
            if TWITCH_CURRENT_TOKEN is None:
                # can't log in, access is denied
                return '[Twitch] Failed to authenticate, cannot use API'
        else:
            return '[Twitch] Unknown API error'

    # try to download user data...
    data = twitch_user_info(inp)
    if 'data' not in data:
        return "[Twitch] Unknown API response, can't get user info"

    data = data['data'][0]  # top tier code right here
    u_id = data.get('id', 0)
    u_name = data.get('display_name', 'Unknown')
    u_user = data.get('login', 'unknown')
    #u_desc = data.get('description', 'None')
    #u_type = data.get('broadcaster_type', 'normal')
    #u_creation = data.get('created_at', '1980-01-01T00:00:00Z')
    #u_views = data.get('view_count', 0)

    # try to download channel info...
    data = twitch_chan_info(u_id)

    if 'data' not in data:
        return "[Twitch] Unknown API response, can't get channel info"

    data = data['data'][0]
    c_title = data.get('title', 'Untitled')
    c_game = data.get('game_name', 'Unknown game')
    c_lang = data.get('broadcaster_language', 'unknown')

    return f'[Twitch] \x02{u_name}\x02 https://twitch.tv/{u_user} was last seen streaming \x02{c_game}\x02 titled "{c_title}" ({c_lang})'


@hook.regex(*TWITCH_RE)
def twitch_urls(match, bot=None, reply=None):
    user = match.group(2)
    reply(f'twitch-senpai pls get me info on {user},,,,')  # intentional, do not delete, very good code right here
    return twitch(user, bot, reply)
