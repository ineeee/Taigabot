# radio plugin rewritten by ine (2020?)
# updated 04/2022

from util import hook
from bs4 import BeautifulSoup
from utilities import request

# all icecast 2.4+ servers support the /status-json.xsl api
radios = {
    'r/a/dio': {
        'name': 'R/a/dio',
        'api': 'https://stream.r-a-d.io/status-json.xsl',
        'homepage': 'https://r-a-d.io/',
        'source': 'main.mp3'
    },

    'eden': {
        'name': 'Eden of the west Public Radio',
        'api': 'https://www.edenofthewest.com/radio/8000/status-json.xsl',
        'homepage': 'https://www.edenofthewest.com/',
        'source': 'radio.mp3'
    },

    'chiru': {
        'name': 'chiru.no',
        'api': 'https://chiru.no:8080/status-json.xsl',
        'homepage': 'https://chiru.no/',
        'source': 'stream.mp3',
    }
}


@hook.command
def radio(id):
    if id == "":
        return "pick a radio: " + ", ".join(list(radios.keys()))

    if id not in radios:
        return "we dont support that radio. try one of the following: " + ", ".join(list(radios.keys()))

    radio = radios[id]

    try:
        data = request.get_json(radio['api'])
    except ValueError:
        return "the radio " + id + " has some server issues right now. try again later"

    sources = data.get('icestats', {}).get('source', False)

    if sources is False:
        return "the radio " + id + " is offline"

    def build_message(source):
        title = source.get('title', 'Untitled')
        listeners = source.get('listeners', 0)
        #genre = sourc.get('genre', 'unknown')
        return u'{} is playing \x02{}\x02 for {} listeners. listen: {}'.format(id, title, listeners, radio['homepage'])

    # the icecast api returns either one object (for one stream)
    # or a list of sources (for multiple streams available)
    if isinstance(sources, dict):
        if sources.get('listenurl', '').endswith(radio['source']):
            return build_message(sources)

    elif isinstance(sources, list):
        for source in sources:
            if source.get('listenurl', '').endswith(radio['source']):
                return build_message(source)

    # didn't find it
    return "the radio " + id + " is offline"


@hook.command
def aradio(inp):
    return radio('r/a/dio')


# fallback because chiru.no's api sometimes returns broken json
# as of 2022 jesus' server runs icecast 2.4.4 so the json api actually works
# still leaving this here
@hook.command(autohelp=False)
@hook.command('mutantradio', autohelp=False)
def muradio(inp):
    "radio [url]-- Returns current mutantradio song"
    url = 'https://chiru.no:8080/status.xsl'
    page = request.get_text(url)
    soup = BeautifulSoup(page, 'lxml')
    stats = soup.find_all('td', 'streamstats')
    # for i in stats:
    #     print i
    # print stats[2], stats[4], stats[5]
    listeners = stats[2].text
    genre = stats[4].text
    # url = stats[5].text
    song = stats[6].text.encode('utf-8').strip()
    return u"[muradio] Playing: {}, Genre: {}, Listening: {}, URL: https://chiru.no/".format(song, genre, listeners)
