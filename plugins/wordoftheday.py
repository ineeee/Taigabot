# word of the day plugin by ine (2020)
# checked 04/2023
from util import hook
from utilities import request, iterable
from bs4 import BeautifulSoup


@hook.command()
def wordoftheday(inp):
    """wordoftheday -- finds an interesting word for today in merriam-webster.com"""
    html = request.get('https://www.merriam-webster.com/word-of-the-day')
    soup = BeautifulSoup(html)

    word = soup.find('div', attrs={'class': 'word-and-pronunciation'}).find('h2').text
    paragraphs = soup.find('div', attrs={'class': 'wod-definition-container'}).find_all('p')

    definitions = []

    for paragraph in iterable.limit(4, paragraphs):
        definitions.append(paragraph.text.strip())

    definitions = '; '.join(definitions)
    output = f'The word of the day is \x02{word}\x02: {definitions}'

    if len(output) > 240:
        output = output[:240] + '... More at https://www.merriam-webster.com/word-of-the-day'

    return output
