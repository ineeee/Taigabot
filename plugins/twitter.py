import re

from utilities.request import get_json

from util import hook


ADRIFTOAPI = 'https://tweet-reader.onrender.com'
TWEET_RE = (r'https?://(twitter|x).com/([-_a-zA-Z0-9]+)/status/(\d+)', re.I)
PROFILE_RE = (r'https?://(twitter|x).com/([-_a-zA-Z0-9]+)(?=$|/[^s])', re.I)
CHAR_LIMIT = 340


def get_tweet(id):
    data = get_json(ADRIFTOAPI + '/get_tweet/' + id)

    if data['status'] != 'success':
        return 'api error'

    user_handle = data['user']['screen_name']
    user_name = data['user']['name']
    text = data.get('text', '').replace('\n', '  ')
    date = data['created_at']

    if data['favorite_count'] == 0 and data['retweet_count'] == 0:
        stats = f"Posted at {date}"
    else:
        stats = f"Posted at {date}, {data['favorite_count']} favs, {data['retweet_count']} retweets"

    if len(text) > CHAR_LIMIT:
        text = text[:CHAR_LIMIT] + '...'

    return f'@\x02{user_handle}\x02 ({user_name}) {text} ({stats})'


def get_profile(id):
    data = get_json(ADRIFTOAPI + '/get_user/' + id)

    if data['status'] != 'success':
        return 'api error'

    user_handle = data['screen_name']
    user_name = data['name']
    desc = data.get('description', '').replace('\n', '  ')

    if len(desc) > CHAR_LIMIT:
        desc = desc[:CHAR_LIMIT] + '...'

    return f'@\x02{user_handle}\x02 ({user_name}) {desc}'


@hook.regex(*TWEET_RE)
def tweet_url(match):
    #url_user = match.group(2)
    url_id = match.group(3)

    output = get_tweet(url_id)
    return f'[Twitter] {output}'


@hook.regex(*PROFILE_RE)
def profile_url(match):
    url_user = match.group(2)

    output = get_profile(url_user)
    return f'[Twitter] {output}'


@hook.command('tw')
@hook.command('twatter')
@hook.command('twinfo')
@hook.command('twuser')
@hook.command
def twitter(inp):
    """twitter <user> -- Gets profile name and description on <user>."""
    output = get_profile(inp)
    return f'[Twitter] {output}'
