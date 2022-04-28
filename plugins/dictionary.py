# dictionary and etymology plugin by ine (2020)
# updated 04/2022
from util import hook
from utilities import request, formatting
from bs4 import BeautifulSoup

dict_url = 'https://ninjawords.com/'
etym_url = 'https://www.etymonline.com/word/'


@hook.command('dictionary')
@hook.command
def define(inp):
    "define <word> -- Fetches definition of <word>."

    word = request.urlencode(inp)
    html = request.get(dict_url + word)
    soup = BeautifulSoup(html, 'lxml')

    definitions = soup.find_all('dd')

    if len(definitions) == 0:
        return "Definition not found"

    output = 'Definition of "' + inp + '":'

    # used to number the many definitions
    i = 1

    for definition in definitions:
        if 'article' in definition['class']:
            text = formatting.compress_whitespace(definition.text.strip())
            output += ' \x02' + text + '\x02'
            i = 1

        elif 'entry' in definition['class']:
            definition = definition.find('div', attrs={'class': 'definition'})
            text = formatting.compress_whitespace(definition.text.strip())
            # 0xb0 is &deg;, &#176; the "°" symbol
            output += text.replace(u'\xb0', ' \x02{}.\x02 '.format(i))
            i = i + 1

        # theres 'synonyms' and 'examples' too

    # arbitrary length limit
    if len(output) > 320:
        output = output[:320] + '\x0f... More at https://en.wiktionary.org/wiki/{}'.format(word)

    return output


@hook.command
def etymology(inp):
    "etymology <word> -- Retrieves the etymology of <word>."

    word = request.urlencode(inp)
    html = request.get(etym_url + word)
    soup = BeautifulSoup(html, 'lxml')
    # the page uses weird class names like "section.word__definatieon--81fc4ae"
    # if it breaks change the selector to [class~="word_"]
    results = soup.select('div[class^="word"] section[class^="word__def"] > p')

    if len(results) == 0:
        return 'No etymology found for ' + inp

    output = u'Ethymology of "' + inp + '":'
    i = 1

    for result in results:
        text = formatting.compress_whitespace(result.text.strip())
        output += u' \x02{}.\x02 {}'.format(i, text)
        i = i + 1

    if len(output) > 200:
        output = output[:200] + '\x0f... More at https://www.etymonline.com/word/{}'.format(word)

    return output
