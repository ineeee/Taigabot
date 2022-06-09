# convenience wrapper for urllib2 & friends
from builtins import chr
from http.cookiejar import CookieJar
import json
import urllib.request, urllib.parse, urllib.error
import re
from urllib.parse import quote_plus as _quote_plus

from lxml import etree, html
from bs4 import BeautifulSoup

ua_firefox = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/50.0 Firefox/50.0'
ua_old_firefox = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6'
ua_internetexplorer = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
ua_chrome = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4'

jar = CookieJar()


def get(*args, **kwargs):
    return open(*args, **kwargs).read()


def get_url(*args, **kwargs):
    return open(*args, **kwargs).geturl()


def get_html(*args, **kwargs):
    return html.fromstring(get(*args, **kwargs))


def get_soup(*args, **kwargs):
    return BeautifulSoup(get(*args, **kwargs), 'lxml')


def get_xml(*args, **kwargs):
    return etree.fromstring(get(*args, **kwargs))


def get_json(*args, **kwargs):
    return json.loads(get(*args, **kwargs))


def open(url, query_params=None, user_agent=None, post_data=None,
         referer=None, get_method=None, cookies=False, **kwargs):

    if query_params is None:
        query_params = {}

    if user_agent is None:
        user_agent = ua_firefox

    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    request = urllib.request.Request(url, post_data)

    if get_method is not None:
        request.get_method = lambda: get_method

    request.add_header('User-Agent', user_agent)

    if referer is not None:
        request.add_header('Referer', referer)

    if cookies:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    else:
        opener = urllib.request.build_opener()

    return opener.open(request)


def prepare_url(url, queries):
    if queries:
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

        query = dict(urllib.parse.parse_qsl(query))
        query.update(queries)
        query = urllib.parse.urlencode(dict((key, value) for key, value in list(query.items())))

        url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

    return url


def quote_plus(s):
    return _quote_plus(s)


def strip_html(html):
    tag = False
    quote = False
    out = ""

    for c in html:
        if c == '<' and not quote: tag = True
        elif c == '>' and not quote: tag = False
        elif (c == '"' or c == "'") and tag: quote = not quote
        elif not tag: out = out + c

    return out


def decode_html(string):
    import re
    entity_re = re.compile(r'&(#?)(\d{1,5}|\w{1,8});')

    def substitute_entity(match):
        from html.entities import name2codepoint as n2cp
        ent = match.group(2)
        if match.group(1) == "#":
            return chr(int(ent))
        else:
            cp = n2cp.get(ent)
            if cp:
                return chr(cp)
            else:
                return match.group()

    return entity_re.subn(substitute_entity, string)[0]


def clean_html(string):
    import html.parser
    h = html.parser.HTMLParser()
    return h.unescape(string)


def process_text(string):
    try: string = string.replace('<br/>', '  ').replace('\n', '  ')
    except: pass
    string = re.sub(r'&gt;&gt;\d*[\s]', '', string)
    string = re.sub(r'(&gt;&gt;\d*)', '', string)
    try: string = strip_html(string)
    except: pass
    try: string = decode_html(string)
    except: pass
    try: string = string.strip()
    except: pass
    string = re.sub(r'[\s]{3,}', '  ', string)
    return string


def get_element(soup, element, idclass=None, selector=None):
    if idclass: result = soup.find(element, {idclass: selector}).renderContents().strip()
    else: result = soup.find(element).renderContents().strip()
    return process_text(result)
