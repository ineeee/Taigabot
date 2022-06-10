import random
import re
import time

from util import hook, http, timeformat

#youtube_re = (r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)'
#              '([-_a-zA-Z0-9]+)', re.I)
youtube_re = (r'((https?://)?(www\.)?(?:youtube.*?(?:v=|/v/)|youtu\.be/)([-_a-zA-Z0-9]+)?(.*))',
              re.I)

base_url = 'https://www.googleapis.com/youtube/v3/'
search_api_url = base_url + 'search?part=id,snippet'
api_url = base_url + 'videos?part=snippet,statistics,contentDetails'


def plural(num=0, text=''):
    return "{:,} {}{}".format(num, text, 's'[num == 1:])


def get_video_description(key, video_id, bot):
    try:
        request = http.get_json(api_url, key=key, id=video_id)
    except Exception:
        key = bot.config.get("api_keys", {}).get("public_google_key")
        request = http.get_json(api_url, key=key, id=video_id)

    if request.get('error'):
        return

    if request.get('pageInfo', {}).get('totalResults') == 0:
        return

    data = request['items'][0]

    title = [_f for _f in data['snippet']['title'].split(' ') if _f]
    title = ' '.join([s.strip() for s in title])
    out = u'\x02{}\x02'.format(title)

    try:
        data['contentDetails'].get('duration')
    except KeyError:
        return out

    length = data['contentDetails']['duration']
    timelist = re.findall(r'(\d+[DHMS])', length)

    seconds = 0
    for t in timelist:
        t_field = int(t[:-1])
        if t[-1:] == 'D': seconds += 86400 * t_field
        elif t[-1:] == 'H': seconds += 3600 * t_field
        elif t[-1:] == 'M': seconds += 60 * t_field
        elif t[-1:] == 'S': seconds += t_field

    out += ' - length \x02{}\x02'.format(timeformat.format_time(seconds, simple=True))

    try:
        data['statistics']
    except KeyError:
        return out

    stats = data['statistics']

    views = int(stats['viewCount'])
    out += ' - \x02{:,}\x02 {}{}'.format(views, 'view', 's'[views == 1:])

    uploader = data['snippet']['channelTitle']

    try:
        upload_time = time.strptime(data['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.000Z")
    except Exception:
        upload_time = time.strptime(data['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
    out += ' - \x02{}\x02 on \x02{}\x02'.format(uploader, time.strftime("%Y.%m.%d", upload_time))

    try:  # ????
        data['contentDetails']['contentRating']
        if data['contentDetails']['contentRating'] == {}:
            return out
    except KeyError:
        return out

    out += ' - \x034NSFW\x02'

    return out


@hook.command('ytr', autohelp=False)
def randomtube(inp, bot=None):
    """randomtube -- Returns random youtube link from old logs."""
    with open('plugins/data/youtube.txt', 'r') as f:
        urllist = f.read().split('\n')
        url = random.choice(urllist)
        f.close()
        return f'A random, secret youtube video: {url}'


@hook.regex(*youtube_re)
def youtube_url(match, bot=None, chan=None):
    key = bot.config.get("api_keys", {}).get("google")

    return get_video_description(key, match.group(4), bot)


@hook.command('yt')
@hook.command('hooktube')
@hook.command('ht')
@hook.command
def youtube(inp, bot=None, input=None):
    """youtube <query> -- Returns the first YouTube search result for <query>."""
    key = bot.config.get('api_keys', {}).get('google')

    try:
        request = http.get_json(search_api_url, key=key, type='video', q=inp)
    except Exception:
        key = bot.config.get('api_keys', {}).get('public_google_key')
        request = http.get_json(search_api_url, key=key, type='video', q=inp)

    if 'error' in request:
        return 'Error performing search.'

    if request['pageInfo']['totalResults'] == 0:
        return 'No results found.'

    video_id = request['items'][0]['id']['videoId']
    if input['trigger'] == 'hooktube' or input['trigger'] == 'ht':
        return get_video_description(key, video_id, bot) + f' - http://hooktube.com/{video_id}'
    else:
        return get_video_description(key, video_id, bot) + f' - https://youtu.be/{video_id}'


@hook.command('ytime')
@hook.command
def youtime(inp, bot=None):
    """youtime <query> -- Gets the total run time of the first YouTube search result for <query>."""
    key = bot.config.get("api_keys", {}).get("google")
    request = http.get_json(search_api_url, key=key, q=inp, type='video')

    if 'error' in request:
        return 'Error performing search.'

    if request['pageInfo']['totalResults'] == 0:
        return 'No results found.'

    video_id = request['items'][0]['id']['videoId']

    request = http.get_json(api_url, key=key, id=video_id)

    data = request['items'][0]

    length = data['contentDetails']['duration']
    timelist = re.findall(r'(\d+[DHMS])', length)

    seconds = 0
    for t in timelist:
        t_field = int(t[:-1])
        if t[-1:] == 'D': seconds += 86400 * t_field
        elif t[-1:] == 'H': seconds += 3600 * t_field
        elif t[-1:] == 'M': seconds += 60 * t_field
        elif t[-1:] == 'S': seconds += t_field

    views = int(data['statistics']['viewCount'])
    total = int(seconds * views)

    length_text = timeformat.format_time(seconds, simple=True)
    total_text = timeformat.format_time(total, accuracy=8)

    return 'The video \x02{}\x02 has a length of {} and has been viewed {:,} times for ' \
            'a total run time of {}!'.format(data['snippet']['title'], length_text, views, total_text)


ytpl_re = (r'(.*:)//(www.youtube.com/playlist|youtube.com/playlist)(:[0-9]+)?(.*)', re.I)


@hook.regex(*ytpl_re)
def youtubeplaylist_url(match):
    location = match.group(4).split("=")[-1]

    try:
        soup = http.get_soup("https://www.youtube.com/playlist?list=" + location)
    except Exception:
        return "\x034\x02Invalid response."

    title = soup.find('title').text.split('-')[0].strip()
    author = soup.find('img', {'class': 'channel-header-profile-image'})['title']
    numvideos = soup.find('ul', {'class': 'pl-header-details'}).findAll('li')[1].string
    numvideos = re.sub(r"\D", "", numvideos)
    views = soup.find('ul', {'class': 'pl-header-details'}).findAll('li')[2].string
    views = re.sub(r"\D", "", views)

    return "\x02{}\x02 - \x02{}\x02 views - \x02{}\x02 videos - \x02{}\x02".format(
        title, views, numvideos, author)
