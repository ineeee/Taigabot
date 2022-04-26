# us debt plugin by ine (2020)
# checked 04/2022
from util import hook
from utilities import request
from bs4 import BeautifulSoup


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    query = soup.find(id='debtDisplay')

    if query is None:
        return "unknown"
    else:
        return "$" + query.text


@hook.command(autohelp=False)
def debt(inp):
    """debt -- returns the us national debt"""

    url = "https://commodity.com/data/usa/debt-clock/"
    html = request.get(url)
    amount = parse(html)

    return "Current US Debt: \x02{}\x02".format(amount)
