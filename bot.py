#!/usr/bin/env python3

#    _        _             _           _
#   | |      (_)           | |         | |
#   | |_ __ _ _  __ _  __ _| |__   ___ | |_
#   | __/ _` | |/ _` |/ _` | '_ \ / _ \| __|
#   | || (_| | | (_| | (_| | |_) | (_) | |_
#    \__\__,_|_|\__, |\__,_|_.__/ \___/ \__|
#                __/ |
#               |___/     irc bot

__author__ = 'inexistence'
__credits__ = [
    # the og guys (i think)
    'infinity', 'thenoodle', '_frozen', 'rmmh',
    # much love weds <3 kept this shit running for many years
    'wednesday', 'frozenpigs',
    # we mantain this bot now
    '676339784', 'adedomin', 'ararouge', 'eskimo', 'blompf', 'DemonOnFishy'
]
__license__ = 'GPL v3'

import os
import queue
import sys
import time
import platform

from core.bot import Bot

if not sys.version_info >= (3, 9):
    print('Taigabot only runs on python 3.9+')
    sys.exit(1)

sys.stdout.reconfigure(line_buffering=True)

print('Taigabot <https://github.com/inexist3nce/Taigabot>')

sys.path += ['plugins']  # so 'import hook' works without duplication
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory

# print debug info
opsys = platform.platform()
python_imp = platform.python_implementation()
python_ver = platform.python_version()
architecture = ' '.join(platform.architecture())

print(f'Operating System: {opsys}, Python {python_imp} {python_ver}, Architecture: {architecture}')

bot = Bot()
bot.ensure_files()

print('Loading plugins...')

# bootstrap the reloader
# afaik this basically "includes" the file right in here, same namespace
reloader_path = os.path.join('core', 'reload.py')
eval(compile(open(reloader_path, 'r').read(), reloader_path, 'exec'))

reload(init=True)
bot.load_config()

print('Connecting to IRC...')

try:
    for name, conf in list(bot.config['connections'].items()):
        print('Connecting to server: %s' % conf['server'])
        if conf.get('ssl'):
            bot.conns[name] = SSLIRC(name,
                                     conf['server'],
                                     conf['nick'],
                                     conf=conf,
                                     port=conf.get('port', 6697),
                                     channels=conf['channels'],
                                     ignore_certificate_errors=conf.get('ignore_cert', True))
        else:
            bot.conns[name] = IRC(name,
                                  conf['server'],
                                  conf['nick'],
                                  conf=conf,
                                  port=conf.get('port', 6667),
                                  channels=conf['channels'])
except Exception as fatal:
    print('ERROR: exception caught while creating the connection')
    raise fatal
    sys.exit(1)


print('Connection(s) made, starting main loop.')

while True:
    reload()  # these functions only do things
    bot.load_config()  # if changes have occured

    for conn in list(bot.conns.values()):
        try:
            out = conn.out.get_nowait()
            main(conn, out)
        except queue.Empty:
            pass
    while all(conn.out.empty() for conn in list(bot.conns.values())):
        try:
            time.sleep(.1)
        except KeyboardInterrupt:
            print('Caught keyboard interrupt, exiting')
            sys.exit(0)
