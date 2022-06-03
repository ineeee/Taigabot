#!/usr/bin/env python2.7

__author__ = "InfinityLabs"
__authors__ = ["Infinity"]
__copyright__ = "Copyright 2013, InfinityLabs"
__copyright__ = "Copyright 2012, ClouDev"
__credits__ = ["infinity","thenoodle", "_frozen", "rmmh"]
__license__ = "GPL v3"
__version__ = "DEV"
__maintainer__ = "InfinityLabs"
__email__ = "root@infinitylabs.us"
__status__ = "Development"

import os
import Queue
import sys
import time
import platform

if not sys.version_info >= (2, 7):
    print 'Taigabot only runs on python 2.7'
    sys.exit(1)


sys.path += ['plugins']  # so 'import hook' works without duplication
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory


class Bot(object):
    def __init__(self):
        self.start_time = time.time()
        self.conns = {}

print 'Taigabot <https://github.com/inexist3nce/Taigabot>'

# print debug info
opsys = platform.platform()
python_imp = platform.python_implementation()
python_ver = platform.python_version()
architecture = ' '.join(platform.architecture())

print "OS: %s, Python: %s %s, Arch: %s" % (opsys, python_imp, python_ver, architecture)

bot = Bot()

print 'Loading plugins...'

# bootstrap the reloader (why can't we just import this?)
eval(compile(open('core/reload.py', 'U').read(), 'core/reload.py', 'exec'))
reload(init=True)

config()
if not hasattr(bot, 'config'):
    exit()

print 'Connecting to IRC...'

try:
    for name, conf in bot.config['connections'].iteritems():
        print 'Connecting to server: %s' % conf['server']
        if conf.get('ssl'):
            bot.conns[name] = SSLIRC(name,
                                     conf['server'],
                                     conf['nick'],
                                     conf=conf,
                                     port=conf.get('port', 6697),
                                     channels=conf['channels'],
                                     ignore_certificate_errors=conf.get('ignore_cert', True)
                                    )
        else:
            bot.conns[name] = IRC(name,
                                  conf['server'],
                                  conf['nick'],
                                  conf=conf,
                                  port=conf.get('port', 6667),
                                  channels=conf['channels']
                                 )
except Exception as e:
    print 'ERROR: malformed config file', e
    sys.exit(1)

bot.persist_dir = os.path.abspath('persist')
if not os.path.exists(bot.persist_dir):
    os.mkdir(bot.persist_dir)

print 'Connection(s) made, starting main loop.'

while True:
    reload()  # these functions only do things
    config()  # if changes have occured

    for conn in bot.conns.itervalues():
        try:
            out = conn.out.get_nowait()
            main(conn, out)
        except Queue.Empty:
            pass
    while all(conn.out.empty() for conn in bot.conns.itervalues()):
        time.sleep(.1)
