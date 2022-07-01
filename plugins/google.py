import re
from urllib.parse import urlencode, quote_plus

from util import hook
from utilities import formatting, request, services

API_URL = 'https://www.googleapis.com/customsearch/v1'


@hook.command('search')
@hook.command('g')
@hook.command
def google(inp, bot):
    """google <query> -- Returns first google search result for <query>."""
    inp = request.urlencode(inp)

    url = API_URL + '?key={}&cx={}&num=1&safe=off&q={}'
    cx = bot.config['api_keys']['googleimage']
    search = '+'.join(inp.split())
    key = bot.config['api_keys']['google']
    result = request.get_json(url.format(key, cx, search))['items'][0]

    title = result['title']
    content = formatting.remove_newlines(result['snippet'])
    link = result['link']

    try:
        return '{} -- \x02{}\x02: "{}"'.format(services.shorten(link), title, content)
    except Exception:
        return '{} -- \x02{}\x02: "{}"'.format(link, title, content)


@hook.regex(r'^\>(.*\.(gif|jpe?g|png|tiff|bmp))$', re.I)
@hook.command('gi')
def image(inp, bot):
    """image <query> -- Returns the first Google Image result for <query>."""
    if type(inp) is str:
        filetype = None
    else:
        inp, filetype = inp.string[1:].split('.')

    cx = bot.config['api_keys']['googleimage']
    search = inp
    key = bot.config['api_keys']['google']

    if filetype:
        url = API_URL + \
            f'?key={key}&cx={cx}&searchType=image&num=1&safe=off&q={quote_plus(search)}&fileType={quote_plus(filetype)}'
        res = request.get_json(url)
    else:
        url = API_URL + f'?key={key}&cx={cx}&searchType=image&num=1&safe=off&q={quote_plus(search)}'
        res = request.get_json(url)

    # DEBUG
    # print(res)
    if 'items' not in res:
        return "Could not find an image."

    res = res['items'][0]

    result = ''
    if not res['link'].startswith('x-raw-image'):
        result = res['link']
    elif 'image' in res and 'thumbnailLink' in res['image']:
        result = res['image']['thumbnailLink']
    else:
        return "Could not find your image."

    return services.shorten(result)
