" seen.py: written by sklnd in about two beers July 2009"
import time
import re

from util import hook, timesince

db_ready = False


def db_init(db, bot):
    """check to see that our db has the the seen table and return a connection."""
    try:
        db.execute("create table if not exists seen(name, time, quote, chan, host, primary key(name, chan))")
    except Exception as e:
        print("ERROR while setting up seen database")
        raise e

    db.commit()
    db_ready = True


def findnth(source, target, n):
    num = 0
    start = -1
    while num < n:
        start = source.find(target, start + 1)
        if start == -1:
            return -1
        num += 1
    return start


def replacenth(source, old, new, n):
    p = findnth(source, old, n)
    if n == -1:
        return source
    return source[:p] + new + source[p + len(old):]


def correction(input, db, notice, say):
    splitinput = input.msg.split('/')
    nick = input.nick
    num = 1
    if len(splitinput) > 3:
        if ' ' in splitinput[3]:
            nick = splitinput[3].split(' ')[1].strip()
            splitinput[3] = splitinput[3].split(' ')[0].strip()

        if len(splitinput[3]) > 2:
            nick = splitinput[3].strip()
        else:
            if 'g' in splitinput[3]:
                num = 0
            else:
                try:
                    num = int(splitinput[3].strip())
                except Exception:
                    num = 1

    last_message = db.execute("select name, quote from seen where name like ? and chan = ?", (nick.lower(), input.chan.lower())).fetchone()

    if last_message:
        splitinput = input.msg.split("/")
        find = splitinput[1]
        replace = splitinput[2]
        if find in last_message[1]:
            if "\x01ACTION" in last_message[1]:
                msg = last_message[1].replace("\x01ACTION ", "/me ").replace("\x01", "")
            else:
                msg = last_message[1]

            if num == 0:
                say("<{}> {}".format(nick, msg.replace(find, "\x02" + replace + "\x02")))
            else:
                say("<{}> {}".format(nick, replacenth(msg, find, "\x02" + replace + "\x02", num)))
        #else:
            #notice(u"{} can't be found in your last message".format(find))
    else:
        if nick == input.nick:
            notice(u"I haven't seen you say anything here yet")
        else:
            notice(u"I haven't seen {} say anything here yet".format(nick))


@hook.singlethread
@hook.event('PRIVMSG', ignorebots=False)
def seen_sieve(paraml, input=None, db=None, bot=None, notice=None, say=None):
    if not db_ready:
        db_init(db, bot)

    if re.match(r'^(s|S)/.*/.*\S*$', input.msg):
        correction(input, db, notice, say)
        return

    # keep private messages private
    if input.chan[:1] == '#':  # TODO fix this, channels can be &, ~, #
        db.execute("insert or replace into seen(name, time, quote, chan, host) values(?,?,?,?,?)",
                   (input.nick.lower(), time.time(), input.msg.replace('\"', "").replace("'", ""), input.chan, input.mask))
        db.commit()


@hook.command
def seen(inp, nick, chan, db, conn, bot):
    """seen <nick> -- Tell when a nickname was last in active in one of this bot's channels."""

    if conn.nick.lower() == inp.lower():
        return "You need to get your eyes checked."

    if inp.lower() == nick.lower():
        return "Have you looked in a mirror lately?"

    if not db_ready:
        db_init(db, bot)

    seens = db.execute("select name, time, quote from seen where name like ? and chan = ?", (inp, chan)).fetchall()
    last_seen = None
    for i in seens:
        if str(i[0]) == inp.lower():
            last_seen = i
    if last_seen:
        reltime = timesince.timesince(last_seen[1])
        if last_seen[0] != inp.lower():  # for glob matching
            inp = last_seen[0]
        if last_seen[2][0:1] == '\x01':
            print('notelse')
            return '{} was last seen {} ago: * {} {}'.format(inp, reltime, inp,
                                                             last_seen[2][8:-1])
        else:
            return '{} was last seen {} ago saying: {}'.format(inp, reltime, last_seen[2])
    else:
        return "I've never seen {} talking in this channel.".format(inp)
