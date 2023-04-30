# lyrics plugin by ine
# rewritten 04/2022
from util import hook
from utilities import request

API_URL = "https://api.genius.com/search"

@hook.command
def lyrics(inp, bot):
    """lyrics <search> -- Search genius.com for song lyrics"""

    headers = {'Authorization': bot.config['api_keys']['genius']}
    params = {'q': inp}
    data = request.get_json(API_URL, params=params, headers=headers)

    if 'error' in data['meta']:
    	return "Genius lyrics API error"

    if len(data['response']['hits']) == 0:
    	return "Didn't find any lyrics for that"

    # always use the first search result
    song = data['response']['hits'][0]['result']
    title = song['title']
    artist = song['artist_names']
    url = song['url']

    return u'Found a song: "{}" by {}. {}'.format(title, artist, url)
