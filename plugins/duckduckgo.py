#!/usr/bin/env python3
# Copyright (C) 2021  Anthony DeDominic <adedomin@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable, NamedTuple, Optional
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qsl

from util import hook
import requests


SEARCH_ENGINE = "https://html.duckduckgo.com/html/"
LEN_LIMIT = 350


class DdgResult(NamedTuple):
    """Type holding a search engine result."""

    url: str
    snippet: str


def get_real_url(indirected_url: str) -> str:
    """
    Parse the true URL from a search result.

    Args:
        indirected_url: The url from the web search.

    Returns:
        The actual clean URL.

    Raises:
        ValueError for irredemably bad URLs.
    """
    url = ''
    parsed_query = urlparse(indirected_url)
    for k, v in parse_qsl(parsed_query.query):
        if k == 'uddg':
            url = v
            break

    if url == '':
        raise ValueError('Empty query')
    elif url.startswith('https://duckduckgo.com'):
        ad = urlparse(url)
        for k, v in parse_qsl(ad.query):
            if k == 'ad_provider':
                raise ValueError('Ad')
    return url


class DdgQueryParser(HTMLParser):
    """HTMLParser that finds anchor tags with search results."""

    def __init__(self):
        """Set up state of the parser."""
        super().__init__(convert_charrefs=True)
        self._url: str = ''
        self._snippet: str = ''
        self.result: Optional[DdgResult] = None
        self._in_result = False

    def handle_starttag(self, tag, attr):
        """Hunt for anchor tags and transition the state of the parser."""
        if self.result:
            return

        css_class = ''
        href = ''
        for k, v in attr:
            if k == 'class':
                css_class = v
            elif k == 'href':
                href = v

        if tag == 'a' and css_class == 'result__snippet' and href != '':
            try:
                self._url = get_real_url(f'https:{href}')
                self._in_result = True
            except ValueError:
                pass

        # ddg puts <b> tags around our search terms.
        # let us make them bold.
        elif tag == 'b' and self._in_result:
            self._snippet += "\x02"

    def handle_endtag(self, tag):
        """Append a result or do nothing."""
        if tag == 'a' and self._in_result:
            self.result = DdgResult(self._url, self._snippet)
            self._in_result = False

        # Terminate the bold text.
        elif tag == 'b' and self._in_result:
            self._snippet += "\x02"

    def handle_data(self, data):
        """Append snippet text."""
        if self._in_result:
            self._snippet += data


def get_answer(q: str) -> str:
    """
    Search ddg for a given query.

    Args:
        q: The user supplied query.

    Returns:
        Result suitable for emitting to IRC.
    """
    with requests.get(SEARCH_ENGINE,
                      params={'q': q},
                      headers={'User-Agent': 'Taigabot/20220618'},
                      allow_redirects=True,
                      stream=True,
                      timeout=15) as stream:
        parser = DdgQueryParser()
        # Up to 128KiB read.
        for (frag, _) in zip(stream.iter_content(chunk_size=4096), range(10)):
            if not frag:
                break
            parser.feed(frag.decode('utf8'))
            # We only want one result.
            if parser.result:
                break

        if parser.result:
            url, snippet = parser.result
            if len(snippet) > LEN_LIMIT:
                snippet = f'{snippet[0:LEN_LIMIT]}...'
            return f'''{snippet} - {url}'''
        else:
            return 'No result.'


@hook.command('ddg')
def ddg(inp: str, say: Callable):
    """ddg <query> -- search the webs with duckduckgo"""
    query = inp.strip()
    if query == '':
        say('[DDG] no query given')
        return

    try:
        res = get_answer(query)
        say(f'[DDG] {res.lstrip()}')
    except Exception as e:
        say(f'{e} - For query {query}')
