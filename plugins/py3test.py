from util import hook
import os
import sys

# this absolute meme of a plugin outputs irc lines to an unix named pipe,
# which means other software can read irc and interact with taiga

# WARNING this plugin cannot be reloaded
# IT WILL BREAK IF ITS RELOADED

# named pipes go through memory and they never touch the network or the hard drive,
# so data transfers should be pretty much instant with no cpu usage

# TODO find a better way to encode taiga data in a line
# just went with 'unicode unit separator' because its unlikely to be in an irc message
# [0]: command
# [1]: raw irc line

SEPARATOR_UNIT = u'\u241f'
SEPARATOR_RECORD = '\r\n'

BOT_READY = False

FIFO_NAME = 'test-fifo-pipe'
if os.path.exists(FIFO_NAME) != True:
    print("fifo missing, creating")
    os.mkfifo(FIFO_NAME)
else:
    print("fifo already exists, reusing")


def pipe_serialize(command, raw):
    raw = raw.replace(SEPARATOR_UNIT, ' ')

    return SEPARATOR_UNIT.join([
        command,
        raw
    ])


def pipe_unserialize(data):
    (command, raw) = data.split(SEPARATOR_UNIT, 2)
    return command, raw


@hook.command
def py3check(inp):
    return "its working rn with python {}.{}".format(sys.version_info.major, sys.version_info.minor)


def fifo_write(data):
    fifo = open(FIFO_NAME, 'wb')
    fifo.write((unicode(data) + SEPARATOR_RECORD).encode('utf-8'))  # fucking encoding hacks
    fifo.close()


@hook.singlethread
@hook.event('*')
def THE_SUCCING(paraml, input=None, say=None):
    global BOT_READY

    if input.command == '376':
        BOT_READY = True
        return

    if BOT_READY != True:
        return

    testdata = pipe_serialize('irc message', input.raw)

    if input.command == 'PRIVMSG':
        print("data: will write, blocking until something reads")
        fifo_write(testdata)

        print("data: will read, blocking until something writes")
        # encoding: read as bytes
        fifo = open(FIFO_NAME, 'rb')
        data = b""

        while True:
            temp = fifo.read()
            if len(temp) == 0:
                break
            else:
                # encoding: both "data" and "temp" are bytes
                data = data + temp

        print("data: read success, will close")
        fifo.close()

        # encoding: transform bytes to str, then concat into unicode
        say(u"reply says: {}".format(data.decode('utf-8')))
