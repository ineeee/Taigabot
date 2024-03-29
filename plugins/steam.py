import re
from util import hook, http, text
from bs4 import BeautifulSoup
import csv
import io

steam_re = (r'(.*:)//(store.steampowered.com)(:[0-9]+)?(.*)', re.I)


def get_steam_info(url):
    # we get the soup manually because the steam pages have some odd encoding troubles
    page = http.get(url)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")

    name = soup.find('div', {'class': 'apphub_AppName'}).text
    desc = ": " + text.truncate_str(soup.find('div', {'class': 'game_description_snippet'}).text.strip())

    # the page has a ton of returns and tabs
    details = soup.find('div', {'class': 'glance_details'}).text.strip().split(u"\n\n\r\n\t\t\t\t\t\t\t\t\t")
    genre = " - Genre: " + details[0].replace(u"Genre: ", u"")
    date = " - Release date: " + details[1].replace(u"Release Date: ", u"")
    price = ""
    if not "Free to Play" in genre:
        price = " - Price: " + soup.find('div', {'class': 'game_purchase_price price'}).text.strip()

    return name + desc + genre + date + price


@hook.regex(*steam_re)
def steam_url(match):
    return get_steam_info("http://store.steampowered.com" + match.group(4))


@hook.command
def steamsearch(inp):
    """steamsearch <search> -- Search for specified game/trailer/DLC"""
    page = http.get("http://store.steampowered.com/search/?term=" + inp)
    soup = BeautifulSoup(page, 'lxml', from_encoding="utf-8")
    result = soup.find('a', {'class': 'search_result_row'})
    return get_steam_info(result['href']) + " - " + result['href']


gauge_url = "http://www.mysteamgauge.com/search?username={}"

api_url = "http://mysteamgauge.com/user/{}.csv"
steam_api_url = "http://steamcommunity.com/id/{}/?xml=1"


def refresh_data(name):
    http.get(gauge_url.format(name), timeout=25, get_method='HEAD')


def get_data(name):
    return http.get(api_url.format(name))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def unicode_dictreader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield dict([(key.lower(), str(value, 'utf-8')) for key, value in list(row.items())])


@hook.command('sc')
@hook.command
def steamcalc(inp, reply):
    """steamcalc <username> -- Gets value of steam account and total hours played"""

    name = inp.strip()

    try:
        request = get_data(name)
        do_refresh = True
    except (http.HTTPError, http.URLError):
        try:
            reply("Collecting data, this may take a while.")
            refresh_data(name)
            request = get_data(name)
            do_refresh = False
        except (http.HTTPError, http.URLError):
            return "Could not get data for this user."

    csv_data = io.StringIO(request)  # we use StringIO because CSV can't read a string
    reader = unicode_dictreader(csv_data)

    # put the games in a list
    games = []
    for row in reader:
        games.append(row)

    data = {}

    # basic information
    steam_profile = http.get_xml(steam_api_url.format(name))
    try:
        data["name"] = steam_profile.find('steamID').text
        online_state = steam_profile.find('stateMessage').text
    except AttributeError:
        return "Could not get data for this user."

    online_state = online_state.replace("<br/>", ": ")  # will make this pretty later
    data["state"] = text.strip_html(online_state)

    # work out the average metascore for all games
    ms = [float(game["metascore"]) for game in games if is_number(game["metascore"])]
    metascore = float(sum(ms)) / len(ms) if len(ms) > 0 else float('nan')
    data["average_metascore"] = "{0:.1f}".format(metascore)

    # work out the totals
    data["games"] = len(games)

    total_value = sum([float(game["value"]) for game in games if is_number(game["value"])])
    data["value"] = str(int(round(total_value)))

    # work out the total size
    total_size = 0.0

    for game in games:
        if not is_number(game["size"]):
            continue

        if game["unit"] == "GB":
            total_size += float(game["size"])
        else:
            total_size += float(game["size"]) / 1024

    data["size"] = "{0:.1f}".format(total_size)

    reply("{name} ({state}) has {games} games with a total value of ${value}"
           " and a total size of {size}GB! The average metascore for these"
           " games is {average_metascore}.".format(**data))

    if do_refresh:
        refresh_data(name)
