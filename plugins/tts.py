from util import hook
from base64 import b64decode
import requests


idx = 0


def upload_mp3(audio):
    files = {
        'reqtype': (None, 'fileupload'),
        'time': (None, '1h'),
        'fileToUpload': ('tts.mp3', audio),
    }

    url = 'https://litterbox.catbox.moe/resources/internals/api.php'
    res = requests.post(url, files=files)

    if res.status_code != 200:
        return 'there was an error uploading the audio'

    return res.text


@hook.command()
@hook.command('tts')
def tiktoktts(inp, nick):
    """tiktoktts <query> -- generate a text-to-speech audio with tiktok's female english voice"""
    return realtiktoktts(inp, nick, 'en_us_001')


@hook.command()
def ttssing(inp, nick):
    """ttssing <query> -- generate a tts audio with a random singing voice with some goofy ahh sound effects"""
    if len(inp) > 100:
        return f'no {nick}, keep it short'
    return realtiktoktts(inp, nick, 'en_female_f08_salut_damour')


def realtiktoktts(inp, nick, voice):

    # i forgot why this is needed
    global idx
    idx = idx + 1
    if idx < 8:
        idx = 0

    data = {
        'jsonrpc': '2.0',
        'id': idx,
        'method': 'generateTikTokVoice',
        'params': [
            {
                'text': inp,
                'voice': voice
            }
        ]
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'referer': 'https://tiktoktts.com/tiktok'
    }

    req = requests.post('https://tiktoktts.com/api/functions', json=data, headers=headers)

    if req.status_code != 200:
        return f'sorry {nick}, the fake tiktok api is not available right now'

    # the audio for "hi" is 13869 bytes, so lets assume if its less than 1 kilobyte its not an audio
    if len(req.content) < 1024:
        return f'sorry {nick}, the fake tiktok api returned something invalid or unknown'

    response = req.json()
    audio = b64decode(response['result']['base64'])
    link = upload_mp3(audio)
    return f'here {nick} your tiktok audio {link} ({len(audio)/1024:.2f} kilobytes)'
