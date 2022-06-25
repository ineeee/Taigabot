# distance plugin rewritten by ine
# still working as of 04/2022
from util import hook
from utilities import request
from bs4 import BeautifulSoup


def fetch(start: str, dest: str):
    start = request.urlencode(start)
    dest = request.urlencode(dest)
    url = f'https://www.travelmath.com/flying-distance/from/{start}/to/{dest}'
    html = request.get(url)
    return html


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    query = soup.find('h1', {'class': 'main'})
    distance = soup.find('h3', {'class': 'space'})

    if query:
        query = query.get_text().strip()

    if distance:
        distance = distance.get_text().strip()

    return query, distance


@hook.command
def distance(inp):
    """distance <start> to <end> -- Calculate the distance between 2 places."""
    if 'from ' in inp:
        inp = inp.replace('from ', '')

    if ' to ' not in inp:
        return '[Distance] You need to specify 2 places like so: "from place1 to place2"'

    start = inp.split(' to ')[0].strip()
    dest = inp.split(' to ')[1].strip()

    html = fetch(start, dest)
    query, distance = parse(html)

    if not distance:
        return f'[Distance] Could not calculate the distance from "{start}" to "{dest}".'

    return f'[Distance] {query} {distance}'
