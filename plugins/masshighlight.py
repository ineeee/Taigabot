import re

from util import hook, user

global userlist
userlist = {}


@hook.event('353')
def onnames(input, conn=None, bot=None):  # what the fuck...
    global userlist
    inp = re.sub(r'[~&@+%,\.]', '', ' '.join(input))
    match = re.match(r'.*#(\S+)(.*)', inp.lower())
    if match is None:
        return
    chan, users = match.group(1, 2)
    try:
        userlist[chan]
    except Exception:
        userlist[chan] = []
    userlist[chan] = set(userlist[chan]) | set(users.split(' '))


@hook.event("JOIN")
def onjoined_addhighlight(inp, input=None, conn=None, chan=None, raw=None):
    global userlist
    try:
        userlist[input.chan.lower().replace('#', '')].add(input.nick.lower())
    except Exception:
        return


@hook.sieve
def highlight_sieve(bot, input, func, kind, args):
    fn = re.match(r'^plugins.(.+).py$', func._filename)
    if fn.group(1) == 'seen' or fn.group(1) == 'tell' or \
       fn.group(1) == 'ai' or fn.group(1) == 'core_ctcp':
        return input

    global userlist
    try:
        users = userlist[input.chan.lower().replace('#', '')]
    except Exception:
        return input

    inp = set(re.sub('[#~&@+%,\.]', '', input.msg.lower()).split(' '))
    if len(users & inp) >= 5:
        globaladmin = user.is_globaladmin(input.mask, input.chan, bot)
        db = bot.get_db_connection(input.conn)
        channeladmin = user.is_channeladmin(input.mask, input.chan, db)
        if not globaladmin and not channeladmin:
            if len(users & inp) >= 7:
                input.conn.send("MODE {} +b *!*{}".format(input.chan, user.format_hostmask(input.mask)))
            input.conn.send("KICK {} {} :MASSHIGHLIGHTING FAGGOT GET #REKT".format(input.chan, input.nick))
    return input


@hook.command(autohelp=False, adminonly=True)
def users(inp, nick, chan, notice):
    """users -- retrieves and sends notices (for internal use)"""
    notice(' '.join(userlist[chan.replace('#', '')]))
    notice('Users: {}'.format(len(userlist[chan.replace('#', '')])))


@hook.command(autohelp=False, adminonly=True)
def getusers(inp, conn, chan):
    """getusers -- retrieves a list of users currently present in a given channel (for internal use)"""
    if inp:
        chan = inp
    conn.send('NAMES {}'.format(chan))


### dev ###
# @hook.command(autohelp=False,adminonly=True)
# def testcompare(inp, notice):
#     users = 'greenbagels ChanStat Pinyin austin j4jackj uguubot infinity fappyhour takoyaki unfinity themadman Knish Onee-chan'.split(' ')
#     inp = 'infinity uguubot themadman josh test2 test3'.split(' ')
#     a = set(users)
#     b = set(inp)
#     notice(' '.join(a|b))
