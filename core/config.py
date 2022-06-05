import json
import os
import sys


if not os.path.exists('config'):
    print("Please rename 'config.default' to 'config' to set up your bot!")
    print('For help, see https://github.com/inexist3nce/Taigabot')
    print('Thank you for using Taigabot!')
    sys.exit(1)


def config() -> None:
    # reload config from file if file has changed
    config_mtime = os.stat('config').st_mtime
    if bot._config_mtime != config_mtime:
        try:
            bot.config = json.load(open('config'))
            bot._config_mtime = config_mtime
        except ValueError as e:
            print('error: malformed config', e)


bot._config_mtime = 0
