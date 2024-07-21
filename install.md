# taigabot dependencies
taigabot runs on python 3 (only 3.9 or 3.10)

- system dependencies: git, python 3 (with pip, wheel, venv)
- taiga dependencies: lxml, bs4, requests

## instructions

1. install python 3.9 or 3.10 (you need pip, wheel and venv)
2. git clone this repo
3. use a virtual environment
4. install the requirements

last step is to configure the bot:

    cp config.default config
    vi config

you can now run taigabot!

    python3 bot.py


### ubuntu 22.04 and debian 12
these instructions work for ubuntu 22.04 and debian 12. taiga requires python 3.9 to 3.11.

if you install python3-wheel in a x64 system, pip will automatically skip compiling stuff. avoid lxml 5.2.1 since it has weird cpu x64 arch requirements (sse4.2? [see here](https://bugs.launchpad.net/lxml/+bug/2059910)).

    # protip: update ur system
    sudo apt update
    sudo apt upgrade

    # system requirements
    sudo apt install --no-install-recomends git python3 python3-pip python3-wheel python3-venv

    # download taigabot
    git clone https://github.com/ineeee/Taigabot.git
    cd Taigabot

    # create and use a virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # install dependencies
    # OPTIONAL: extras/requirements.txt
    python3 -m pip install -r requirements.txt

    # edit the config file
    cp config.default config
    vi config

    # run the bot
    python3 bot.py


## python dependencies
you __need__ these to run almost all plugins.

    pip install -r requirements.txt

- lxml
- requests
- beautifulsoup4


## specific dependencies
some plugins need extra dependencies, you can read `extra/requirements.txt` for more info. theyre optional, without these the plugins simply wont load.

## api keys
some api keys must be set in the `config` or those plugins won't work

| key name                | plugin                | source |
|-------------------------|-----------------------|--------|
| bitly_api               |                       |        |
| bitly_user              |                       |        |
| darksky                 | weather               | can't get anymore |
| ebay                    |                       |        |
| english_bible           | religion              | [link](https://api.esv.org/docs/) |
| exhentai                |                       |        |
| genius                  |                       |        |
| geoip                   |                       |        |
| google                  | google                |        |
| google2                 |                       |        |
| google3                 |                       |        |
| googleimage             | google                |        |
| iex                     |                       |        |
| lastfm                  |                       |        |
| mc_pass                 |                       |        |
| mc_user                 |                       |        |
| old_pastebin            |                       |        |
| openai_chatgpt          | openai                |        |
| openweathermap          |                       |        |
| papkey                  |                       |        |
| pastebin                |                       |        |
| pirateweather           |                       |        |
| public_google_key       |                       |        |
| rottentomatoes          |                       |        |
| spotify_client_id       |                       |        |
| spotify_client_secret   |                       |        |
| tvdb                    |                       |        |
| twitch_client_id        | twitch                | [link](https://dev.twitch.tv/docs/api#step-1-register-an-application) |
| twitch_client_secret    | twitch                | [link](https://dev.twitch.tv/docs/api#step-1-register-an-application) |
| twitter_access_secret   |                       |        |
| twitter_access_token    |                       |        |
| twitter_consumer_key    |                       |        |
| twitter_consumer_secret |                       |        |
| wolframalpha            | wolframalpha          | [link](https://products.wolframalpha.com/api/) |
| yahoo                   |                       |        |
| yahoo_id                |                       |        |

TODO document this
