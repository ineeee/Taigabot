""" web.py - handy functions for web services """
import requests


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def isgd(url: str):
    """ shortens a URL with the is.gd API """
    req = requests.get("http://is.gd/create.php", params={'format': 'json', 'url': url})

    try:
        json = req.json()
    except ValueError:
        print("[!] ERROR: is.gd returned broken json")
        raise

    if "errorcode" in json:
        raise ShortenError(json["errorcode"], json["errormessage"])
    else:
        return json["shorturl"]


def try_isgd(url):
    return isgd(url)
