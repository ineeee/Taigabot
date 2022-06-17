import requests

user = 'taigabot'

HEADERS = {'User-Agent': 'taigabot, python irc bot'}


def paste_taigalink(text: str, title: str = 'Paste'):
    data = {
        'title': title,
        'uploader': 'taigabot',
        'text': text
    }
    res = requests.post('https://taiga.link/p/upload', headers=HEADERS, data=data)
    return res.text

def paste_litterbox(text: str):

    files = {
        'reqtype': (None, 'fileupload'),
        'time': (None, '1h'),
        'fileToUpload': ('filesss.txt', text),
    }

    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    response = requests.post(url, files=files)

    if response.status_code == 200:
        return response.text

    return "Error uploading text file"


# leaving this one here in case taigalink dies
def paste_pastebin(text: str, title: str = 'Paste', config={}):
    # sadly we need to pass bot.config because of the api keys
    api_key = config.get('api_keys', {}).get('pastebin', False)

    if api_key is False:
        return "no api key found, pls fix config"

    data = {
        'api_dev_key': api_key,
        'api_option': 'paste',
        'api_paste_code': text,
        'api_paste_name': title,
        'api_paste_private': 1,
        'api_paste_expire_date': '1D',
    }

    response = requests.post('https://pastebin.com/api/api_post.php', headers={'User-Agent': fake_ua}, data=data, timeout=12, allow_redirects=True)
    return response.text.strip()


def paste_sprunge(data):
    sprunge_data = {'sprunge': data}
    response = requests.post('http://sprunge.us', data=sprunge_data)
    return response.text.strip()


def shorten_taigalink(url: str):
    data = {'url': url}
    res = requests.post('https://taiga.link/s/short', headers={'User-Agent': 'taigabot'}, data=data)
    return res.text.strip()


# upload any text to pastebin
# please use this function so you don't have to modify 40 plugins when the api changes
def paste(text: str, title: str = 'Paste'):  # paste(*args, **kwargs)?
    return paste_taigalink(text, title)


def shorten(url: str):
    return shorten_taigalink(url)
