import re
import urllib.request
import urllib.error
import urllib.parse
from urllib.parse import urlparse
from html.parser import HTMLParser as HtmlParser

import requests
from bs4 import BeautifulSoup

from util import database, formatting, hook, http

from utilities.formatting import compress_whitespace

MAX_LENGTH = 200
trimlength = 320

IGNORED_HOSTS = [
    '.onion',
    'localhost',
    # these are handled by their respective plugin
    # more info on some other file
    'youtube.com',    # handled by youtube plugin
    'youtu.be',
    'music.youtube.com',
    'vimeo.com',
    'player.vimeo.com',
    'newegg.com',
    'amazon.com',
    # 'reddit.com',
    'hulu.com',
    'imdb.com',
    'soundcloud.com',
    'spotify.com',
    'twitch.tv',
    'twitter.com',

    # handled on mediawiki.py
    'en.wikipedia.org',
    'encyclopediadramatica.wiki',
]

# 'http' + s optional + ':// ' + anything + '.' + anything
LINK_RE = (r'(https?://\S+\.\S*)', re.I)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for br in soup.find_all('br'):
        br.replace_with('\n')

    return soup.get_text()


@hook.regex(*LINK_RE)
def process_url(match, bot=None, chan=None, db=None):
    url = match.group(0)
    parsed = urlparse(url)
    # parsed contains scheme, netloc, path, params, query, fragment

    # skip unwanted hosts
    # most of them are handled somewhere else anyway
    for ignored in IGNORED_HOSTS:
        if ignored in parsed.netloc:
            return

    if 'simg.gelbooru.com' in url.lower():
        return unmatched_url(url, parsed, bot, chan, db)    # handled by Gelbooru plugin: exiting
    elif 'gelbooru.com' in url.lower():
        return    # handled by Gelbooru plugin: exiting
    elif 'craigslist.org' in url.lower():
        return craigslist_url(url)    # Craigslist
    elif 'ebay.com' in url.lower():
        return ebay_url(url, bot)    # Ebay
    elif 'wikipedia.org' in url.lower():
        return wikipedia_url(url)    # Wikipedia
    elif 'hentai.org' in url.lower():
        return hentai_url(url, bot)    # Hentai
    elif 'boards.4chan.org' in url.lower() or 'boards.4channel.org' in url.lower():    # 4chan
        if '#p' in url.lower():
            return fourchanquote_url(url)    # 4chan Quoted Post

        if '/thread/' in url.lower() or '/res/' in url.lower():
            return fourchanthread_url(url)    # 4chan Post

        if '/src/' in url.lower():
            return unmatched_url(url, parsed, bot, chan, db)    # 4chan Image
        else:
            return fourchanboard_url(url)    # 4chan Board
    else:
        return unmatched_url(url, parsed, bot, chan, db)    # process other url


# @hook.regex(*fourchan_re)
def fourchanboard_url(match):
    soup = http.get_soup(match)
    title = soup.title.renderContents().strip()
    return http.process_text("\x02{}\x02".format(title[:trimlength]))


def fourchanapi_get_thread(board: str, thread: str):
    url = f'https://a.4cdn.org/{board}/thread/{thread}.json'
    req = requests.get(url)

    if req.status_code != 200:
        print(f'[ERROR] some 4chan api error happened, http status {req.status_code} ({board}, {thread})')
        return None

    data = req.json()
    return data


# fourchan_re = (r'.*((boards\.)?4chan\.org/[a-z]/res/[^ ]+)', re.I)
# @hook.regex(*fourchan_re)
def fourchanthread_url(match):
    regxp = r'https?:\/\/(boards\.)?4chan(nel)?\.org\/([a-z]+)\/(thread|res)\/([0-9]+)'
    match2 = re.search(regxp, match)

    if match2 is None:
        return

    board, thread = match2.group(3, 5)
    data = fourchanapi_get_thread(board, thread)
    post_op = data.get('posts', [])[0]

    subject = post_op['sub'] if 'sub' in post_op else None
    comment = post_op['com'] if 'com' in post_op else None
    author = post_op['name'] if 'name' in post_op else 'Anonymous'
    tripcode = post_op['trip'] if 'trip' in post_op else None

    output = f'\x02/{board}/'

    if subject:
        output += f' - {subject}'

    output += '\x02 - posted by '

    if tripcode:
        output += f'\x02{author[:80]} {tripcode}\x02'
    else:
        output += f'\x02{author[:80]}\x02'

    if comment:
        comment = html_to_text(comment).replace('\n', '  ')

        # MAX_LENGTH chars max
        if len(comment) > MAX_LENGTH:
            output += f': {comment[:MAX_LENGTH]}...'
        else:
            output += f': {comment}'

    return output


# fourchan_quote_re = (r'>>(\D\/\d+)', re.I)
# fourchanquote_re = (r'.*((boards\.)?4chan\.org/[a-z]/res/(\d+)#p(\d+))', re.I)
# @hook.regex(*fourchanquote_re)
def fourchanquote_url(match):
    regxp = r'https?:\/\/(boards\.)?4chan(nel)?\.org\/([a-z]+)\/(thread|res)\/([0-9]+)#p([0-9]+)'
    match2 = re.search(regxp, match)

    if match2 is None:
        return

    board, threadid, postid = match2.group(3, 5, 6)
    data = fourchanapi_get_thread(board, threadid)
    posts = data.get('posts', [])
    post_op = posts[0]
    post_op_subject = post_op['sub'] if 'sub' in post_op else None

    chosen_post = None

    # try to find the quoted post somewhere in the thread
    for temp in posts:
        if str(temp['no']) == postid:
            chosen_post = temp
            break

    # fuck off if didnt find it
    # maybe someone linked an invalid post? idk
    if chosen_post is None:
        return

    comment = chosen_post['com'] if 'com' in chosen_post else None
    author = chosen_post['name'] if 'name' in chosen_post else 'Anonymous'
    tripcode = chosen_post['trip'] if 'trip' in chosen_post else None

    output = f'\x02/{board}/'

    if post_op_subject:
        output += f' - {post_op_subject}'

    output += '\x02 - reply by '

    if tripcode:
        output += f'\x02{author[:80]} {tripcode}\x02'
    else:
        output += f'\x02{author[:80]}\x02'

    comment = html_to_text(comment).replace('\n', '  ')
    if len(comment) > MAX_LENGTH:
        output += f': {comment[:MAX_LENGTH]}...'
    else:
        output += f': {comment}'

    return output


def craigslist_url(match):
    soup = http.get_soup(match)
    title = soup.find('h2', {'class': 'postingtitle'}).renderContents().strip()
    post = soup.find('section', {'id': 'postingbody'}).renderContents().strip()
    return http.process_text("\x02Craigslist.org: {}\x02 - {}".format(title, post[:trimlength]))


# ebay_item_re = r'http:.+ebay.com/.+/(\d+).+'
def ebay_url(match, bot):
    item = http.get_html(match)
    title = item.xpath("//h1[@id='itemTitle']/text()")[0].strip()
    price = item.xpath("//span[@id='prcIsum_bidPrice']/text()")
    if not price:
        price = item.xpath("//span[@id='prcIsum']/text()")
    if not price:
        price = item.xpath("//span[@id='mm-saleDscPrc']/text()")
    if price:
        price = price[0].strip()
    else:
        price = '?'

    try:
        bids = item.xpath("//span[@id='qty-test']/text()")[0].strip()
    except:
        bids = "Buy It Now"

    feedback = item.xpath("//span[@class='w2b-head']/text()")
    if not feedback:
        feedback = item.xpath("//div[@id='si-fb']/text()")
    if feedback:
        feedback = feedback[0].strip()
    else:
        feedback = '?'

    return http.process_text("\x02{}\x02 - \x02\x033{}\x03\x02 - Bids: {} - Feedback: {}".format(
        title, price, bids, feedback))


def wikipedia_url(match):
    soup = http.get_soup(match)
    title = soup.find('h1', {'id': 'firstHeading'}).renderContents().strip()
    post = soup.find('p').renderContents().strip().replace('\n', '').replace('\r', '')
    return http.process_text("\x02Wikipedia.org: {}\x02 - {}...".format(title, post[:trimlength]))


# hentai_re = (r'(http.+hentai.org/.+)', re.I)
# @hook.regex(*hentai_re)
def hentai_url(match, bot):
    userpass = bot.config.get("api_keys", {}).get("exhentai")
    if "user:pass" in userpass:
        return
    else:
        username = userpass.split(':')[0]
        password = userpass.split(':')[1]
        if not username or not password:
            return    # "error: no username/password set"

    url = match
    loginurl = 'http://forums.e-hentai.org/index.php?act=Login&CODE=01'
    logindata = 'referer=http://forums.e-hentai.org/index.php&UserName={}&PassWord={}&CookieDate=1'.format(
        username, password)

    req = urllib.request.Request(loginurl)
    resp = urllib.request.urlopen(req, logindata)    # POST
    coo = resp.info().getheader('Set-Cookie')    # cookie
    cooid = re.findall('ipb_member_id=(.*?);', coo)[0]
    coopw = re.findall('ipb_pass_hash=(.*?);', coo)[0]

    headers = {
        'Cookie': 'ipb_member_id=' + cooid + ';ipb_pass_hash=' + coopw,
        'User-Agent':
        "User-Agent':'Mozilla/5.2 (compatible; MSIE 8.0; Windows NT 6.2;)",    # wow this code is ass
    }

    request = urllib.request.Request(url, None, headers)
    page = urllib.request.urlopen(request).read()
    soup = BeautifulSoup(page)
    try:
        title = soup.find('h1', {'id': 'gn'}).string
        date = soup.find('td', {'class': 'gdt2'}).string
        rating = soup.find('td', {'id': 'rating_label'}).string.replace('Average: ', '')
        star_count = round(float(rating), 0)
        stars = ""
        for x in range(0, int(star_count)):
            stars = "{}{}".format(stars, ' ')
        for y in range(int(star_count), 5):
            stars = "{}{}".format(stars, ' ')

        return '\x02{}\x02 - \x02\x034{}\x03\x02 - {}'.format(title, stars, date).decode('utf-8')
    except:
        return u'{}'.format(soup.title.string)


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
headers = {'User-Agent': user_agent}


class TitleParser(HtmlParser):
    """Parser Fetching <title> tag contents."""

    def __init__(self):
        """Set up parser."""
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.done = False
        self.title = ''

    def handle_starttag(self, tag, attr):
        """Find title."""
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        """Terminate parser on closing title."""
        if tag == 'title':
            self.in_title = False
            self.done = True

    def handle_data(self, inner_text):
        """Collect title contents."""
        if self.in_title:
            self.title += inner_text


def parse_html(stream, encoding: str = 'utf8'):
    """Parse Title Tags from HTML"""
    parser = TitleParser()
    for chunk, _ in zip(stream.iter_content(chunk_size=4096), range(10)):
        parser.feed(chunk.decode(encoding))
        if parser.done:
            title = compress_whitespace(parser.title)
            return title.strip()

    return 'Untitled'


def unmatched_url(url, parsed, bot, chan, db):
    disabled_commands = database.get(db, 'channels', 'disabled', 'chan', chan) or []

    # don't bother if the channel has url titles disabled
    if 'urltitles' in disabled_commands:
        return

    # fetch, and hide all errors from the output
    try:
        req = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=8)
    except Exception as e:
        print('[!] WARNING couldnt fetch url')
        print(e)
        return

    # parsing
    domain = parsed.netloc
    content_type = req.headers.get('Content-Type', '')
    size = req.headers.get('Content-Length', 0)
    output = ['[URL]']

    if 'html' in content_type:
        try:
            title = parse_html(req)
        except Exception as e:
            print('[!] WARNING the url caused a parser error')
            print(e)
            title = 'Untitled'

        # fucking cloudflare
        if 'Attention Required! | Cloudflare' in title:
            return

        output.append(title)

    else:
        if 'filesize' in disabled_commands:
            return

        # very common mime types
        if 'image/' in content_type:
            output.append(content_type.replace('image/', '') + ' image,')
        elif 'video/' in content_type:
            output.append(content_type.replace('video/', '') + ' video,')
        elif 'text/' in content_type:
            output.append('text file,')
        elif 'application/octet-stream' == content_type:
            output.append('binary file,')
        elif 'audio/' in content_type:
            output.append('audio file,')

        # other mime types
        elif 'application/vnd.' in content_type:
            output.append('unknown binary file,')
        elif 'font/' in content_type:
            output.append('font,')

        # i dunno
        else:
            output.append(content_type + ' file,')

        try:
            size = int(size)
        except TypeError:
            size = 0

        # some pages send exactly 503 or 513 bytes of empty padding as an
        # internet explorer 5 and 6 workaround, but since that browser is
        # super dead this should probably be removed.
        # more at https://stackoverflow.com/a/11544049/4301778
        if size == 0 or size == 503 or size == 513:
            output.append('unknown size')
        else:
            output.append('size: ' + formatting.filesize(size))

    # output formatting
    output = ' '.join(output)

    if len(output) > MAX_LENGTH:
        output = output[:MAX_LENGTH] + '...'

    # add domain to the end
    output = "{} ({})".format(output, domain)

    # show error codes if they appear
    if req.status_code >= 400 and req.status_code < 600:
        output = '{} (error {})'.format(output, req.status_code)

    return output
