from util import hook, http, web, text
from urllib.parse import urlencode
import re

sc_re = (r'(.*:)//(www.)?(soundcloud.com)(.*)', re.I)
api_url = "http://api.soundcloud.com"
sndsc_re = (r'(.*:)//(www.)?(snd.sc)(.*)', re.I)


def soundcloud(url, api_key):
    data = http.get_json(api_url + '/resolve.json?' + urlencode({'url': url, 'client_id': api_key}))

    desc = ""
    if data['description']: desc = u": {} ".format(text.truncate_str(data['description'], 50))

    genre = ""
    if data['genre']: genre = u"- Genre: \x02{}\x02 ".format(data['genre'])

    duration = ""
    if data['duration']:
        tracklength = float(data['duration']) / 60000
        tracklength = re.match('(.*\...)', str(tracklength)).group(1)
        if tracklength: duration = u" {} mins -".format(tracklength)


    url = web.try_isgd(data['permalink_url'])

    return u"SoundCloud track: \x02{}\x02 by \x02{}\x02 {}{}-{} {} plays, {} downloads, {} comments - {}".format(
        data['title'], data['user']['username'], desc, genre, duration, data['playback_count'], data['download_count'],
        data['comment_count'], url)


@hook.regex(*sc_re)
def soundcloud_url(match, bot=None):
    api_key = bot.config.get("api_keys", {}).get("soundcloud")
    if not api_key:
        print("Error: no api key set")
        return None
    url = match.group(1).split(' ')[-1] + "//" + (match.group(2) if match.group(2) else "") + match.group(3) + \
          match.group(4).split(' ')[0]
    return soundcloud(url, api_key)


@hook.regex(*sndsc_re)
def sndsc_url(match, bot=None):
    api_key = bot.config.get("api_keys", {}).get("soundcloud")
    if not api_key:
        print("Error: no api key set")
        return None
    url = match.group(1).split(' ')[-1] + "//" + (match.group(2) if match.group(2) else "") + match.group(3) + \
          match.group(4).split(' ')[0]
    return soundcloud(http.open(url).url, api_key)
