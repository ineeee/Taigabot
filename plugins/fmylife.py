from __future__ import print_function
# fuck my life plugin by ine (2020)
# updated 04/2022
from util import hook
from utilities import request
from bs4 import BeautifulSoup

cache = []


def refresh_cache():
    print("[+] refreshing fmylife cache")
    html = request.get('https://www.fmylife.com/random')
    soup = BeautifulSoup(html, 'lxml')
    posts = soup.find_all('a', attrs={'class': 'block text-blue-500 my-4'})

    for post in posts:
        id = post['href'].split('_')[1].split('.')[0]
        text = post.text.strip()
        cache.append((id, text))


@hook.command("fmylife", autohelp=False)
@hook.command(autohelp=False)
def fml(inp):
    "fml -- Gets a random quote from fmyfife.com."

    if len(cache) < 2:
        refresh_cache()

    id, text = cache.pop()
    return '(#{}) {}'.format(id, text)
