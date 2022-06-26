# Plugin made by Infinity, Lukeroge and neersighted
from __future__ import division
from past.utils import old_div
import re
from time import sleep

from util import database, hook, scheduler, user

# oh my fucking god
TRUE_ISH = 'yeah'
FALSE_ISH = 'nope'


# \binfinity@[^\s]*like.lolis\b
@hook.command(autohelp=False, adminonly=True)
def mask(inp):
    return re.sub(r'((?:@)[^@\.]+\d{2,}([^\.]?)+\.)', '*',
                  inp.replace('@', '@@')).replace('@@', '@').lower().strip()


def format_hostmask(inp):
    "format_hostmask -- Returns a nicks userhost"
    return re.sub(r'(@[^@\.]+\d{2,}([^\.]?)+\.)', '*',
                  inp.replace('@', '@@')).replace('@@', '@').lower().strip()


def compare_hostmasks(hostmask, matchmasks):
    for mask in re.findall(r'(\b\S+\b)', ' '.join(matchmasks)):
        mask = '^*{}$'.format(mask).replace('.', r'\.').replace('*', '.*')
        if bool(re.match(mask, hostmask)):
            print('{} - {}'.format(mask, hostmask))
            return True
    return False


def is_globaladmin(hostmask, chan, bot):
    globaladmins = bot.config.get('admins', [])
    if globaladmins: return compare_hostmasks(hostmask, globaladmins)


def is_channeladmin(hostmask, chan, db):
    channeladmins = database.get(db, 'channels', 'admins', 'chan',
                                 chan).split(' ')
    if channeladmins: return compare_hostmasks(hostmask, channeladmins)


@hook.command(autohelp=False, channeladminonly=True)
def match(inp, chan, bot, input, db):
    if inp: mask = user.get_hostmask(inp, db)
    else: mask = input.mask
    # hostmask = format_hostmask(mask)

    channeladmin = user.is_channeladmin(mask, chan, db)
    globaladmin = user.is_globaladmin(mask, chan, bot)
    if channeladmin and globaladmin:
        return "Global & Local Admin: ({})".format(mask)
    elif channeladmin:
        return "Local Admin: {}".format(mask)
    elif globaladmin:
        return "Global Admin: {}".format(mask)

    return '{}: is not an admin'.format(mask)
    # return re.sub(r'(@[^@\.]+\d{2,}([^\.]?)+\.)','*',inp.replace('@','@@')).replace('~','').replace('@@','@').lower().strip()


######################
### Admin Commands ###


@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def admins(inp, notice, chan, db):
    """admins [channel] -- Lists admins on channel."""
    admins = database.get(db, 'channels', 'admins', 'chan', chan)

    if admins:
        notice(f'[{chan}]: Admins are: {admins}')
    else:
        notice(f'[{chan}]: No nicks/hosts are currently admins.')

    return


@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def admin(inp, notice, chan, db):
    """admin [channel] <add|del> <nick|host> -- Makes the user an admin."""

    if len(inp) < 1:
        notice('Missing subcommand. Usage: .admin <add/del> <nick/*>')
        return

    admins = database.get(db, 'channels', 'admins', 'chan', chan)
    command = inp.split()[0]
    nicks = inp.split()[1:]

    if command not in ('add', 'del'):
        notice('Unknown subcommand. Usage: .admin <add/del> <nick/*>')
        return

    if len(nicks) < 1:
        notice('Missing nicks. Usage: .admin <add/del> <nick/*>')
        return

    if 'add' in command:
        for nick in nicks:
            nick = user.get_hostmask(nick, db)
            if admins and nick in admins:
                notice(f'[{chan}]: {nick} is already an admin.')
            else:
                admins = '{} {}'.format(nick, admins).replace('False', '').strip()
                database.set(db, 'channels', 'admins', admins, 'chan', chan)
                notice(f'[{chan}]: {nick} is now an admin.')
    elif 'del' in command:
        if '*' in nicks:
            database.set(db, 'channels', 'admins', '', 'chan', chan)
            notice(f'[{chan}]: All admins have been removed.')
            return

        for nick in nicks:
            nick = user.get_hostmask(nick, db)
            if admins and nick in admins:
                admins = ' '.join(admins.replace(nick, '').strip().split())
                database.set(db, 'channels', 'admins', admins, 'chan', chan)
                notice(f'[{chan}]: {nick} is no longer an admin.')
            else:
                notice(f'[{chan}]: {nick} is not an admin.')

    return


######################
### Auto op Commands ###

@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def autoops(inp, notice, chan, db):
    """aops [channel] -- Lists autoops on channel."""

    autoops: str = database.get(db, 'channels', 'autoops', 'chan', chan)
    should_autoop = database.get(db, 'channels', 'autoop', 'chan', chan)
    autoop_status = 'enabled' if should_autoop == TRUE_ISH else 'disabled'

    if autoops:
        notice(f'[{chan}]: Auto ops are {autoop_status} and the list is {autoops}')
    else:
        notice(f'[{chan}]: Auto ops are {autoop_status} but no nicks/hosts are in the list.')
    return


@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def autoop(inp, notice, chan, db):
    """aop [channel] <enable|disable> OR <add|del> <nick|host> -- Add/Del Autoops."""

    if len(inp) < 1:
        notice('Missing subcommand. Usage: .autoop <enable/disable/add/del>')
        return

    autoops = database.get(db, 'channels', 'autoops', 'chan', chan)
    command = inp.split()[0]

    if command not in ('enable', 'disable', 'add', 'del'):
        notice('Unknown subcommand. Usage: .autoop <enable/disable/add/del>')
        return

    if 'enable' in command:
        database.set(db, 'channels', 'autoop', TRUE_ISH, 'chan', chan)
        notice(f'[{chan}]: Autoops is now enabled.')
    elif 'disable' in command:
        database.set(db, 'channels', 'autoop', FALSE_ISH, 'chan', chan)
        notice(f'[{chan}]: Autoops is now disabled.')
    elif 'add' in command:
        nicks = inp.split()[1:]

        if len(nicks) < 1:
            notice('Missing nicks. Usage: .autoop add <nick>')
            return

        for nick in nicks:
            nick = user.get_hostmask(nick, db)
            if autoops and nick in autoops:
                notice(f'[{chan}]: {nick} is already an autoop.')
            else:
                autoops = '{} {}'.format(nick, autoops).replace('False', '').strip()
                database.set(db, 'channels', 'autoops', autoops, 'chan', chan)
                notice(f'[{chan}]: {nick} is now an auto op.')
    elif 'del' in command:
        nicks = inp.split()[1:]

        if '*' in nicks:
            database.set(db, 'channels', 'autoops', '', 'chan', chan)
            notice(f'[{chan}]: All auto ops have been removed.')
            return

        for nick in nicks:
            nick = user.get_hostmask(nick, db)
            if autoops and nick in autoops:
                autoops = ' '.join(autoops.replace(nick, '').strip().split())
                database.set(db, 'channels', 'autoops', autoops, 'chan', chan)
                notice(f'[{chan}]: {nick} is no longer an auto op.')
            else:
                notice(f'[{chan}]: {nick} is not an auto op.')
    return


@hook.event('JOIN')
def event_handle_autoop(inp, input, db, chan, conn, nick):
    should_autoop = database.get(db, 'channels', 'autoop', 'chan', chan)

    if should_autoop != TRUE_ISH:
        # bail if auto_op isnt enabled
        return

    autoops: str = database.get(db, 'channels', 'autoops', 'chan', chan)

    if len(autoops) == 0:
        # bail if the list is empty
        return

    autoops = autoops.split(' ')

    # nick!user@host of the user who just joined
    current_mask = user.format_hostmask(input.mask)

    for mask in autoops:
        if mask == current_mask:
            conn.send(f'MODE {chan} +o {nick}')

    return

################################
### Ignore/Unignore Commands ###


@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def ignored(inp, notice, bot, chan, db):
    """ignored [channel] -- Lists ignored channels/nicks/hosts."""
    ignorelist = database.get(db, 'channels', 'ignored', 'chan', chan)

    if ignorelist:
        notice(f'[{chan}]: Ignored nicks/hosts are: {ignorelist}')
    else:
        notice(f'[{chan}]: No nicks/hosts are currently ignored.')

    return


@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def ignore(inp, notice, bot, chan, db):
    """ignore [channel] <nick|host> -- Makes the bot ignore <nick|host>."""
    ignorelist = database.get(db, 'channels', 'ignored', 'chan', chan)
    targets = inp.split()
    for target in targets:
        target = user.get_hostmask(target, db)
        if user.is_admin(target, chan, db, bot):
            notice(f'[{chan}]: {inp} is an admin and cannot be ignored.')
        else:
            if ignorelist and target in ignorelist:
                notice(f'[{chan}]: {target} is already ignored.')
            else:
                if ignorelist is False:
                    database.set(db, 'channels', 'ignored', target, 'chan', chan)
                else:
                    ignorelist = '{} {}'.format(target, ignorelist)
                    database.set(db, 'channels', 'ignored', ignorelist, 'chan', chan)

                notice(f'[{chan}]: {target} has been ignored.')
    return


@hook.command(permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def unignore(inp, notice, bot, chan, db):
    """unignore [channel] <nick|host> -- Makes the bot listen to <nick|host>."""
    ignorelist = database.get(db, 'channels', 'ignored', 'chan', chan)
    targets = inp.split()
    for target in targets:
        target = user.get_hostmask(target, db)
        if ignorelist and target in ignorelist:
            ignorelist = ' '.join(ignorelist.replace(target, '').strip().split())
            database.set(db, 'channels', 'ignored', ignorelist, 'chan', chan)
            notice(f'[{chan}]: {target} has been unignored.')
        else:
            notice(f'[{chan}]: {target} is not ignored.')
    return


###############################
### Enable/Disable Commands ###


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def disabled(inp, notice, bot, chan, db):
    """disabled [#channel] -- Lists disabled commands/."""
    disabledcommands = database.get(db, 'channels', 'disabled', 'chan', chan)
    disabledglobalcommands = " ".join(bot.config["disabled_commands"])
    if disabledcommands:
        notice(u"[{}]: Disabled commands: Chan: {}, Global: {}".format(
            chan, disabledcommands, disabledglobalcommands))
    else:
        notice(u"[{}]: No commands are currently disabled.".format(chan))
    return


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def disable(inp, notice, bot, chan, db):
    """disable [#channel] <commands> -- Disables commands for a channel.
    (you can disable multiple commands at once)"""

    disabledcommands = database.get(db, 'channels', 'disabled', 'chan', chan)
    targets = inp.split()
    for target in targets:
        if disabledcommands and target in disabledcommands:
            notice(u"[{}]: {} is already disabled.".format(chan, target))
        else:
            if 'disable' in target or 'enable' in target or 'core_admin' in target or 'plez' in target:
                notice(u"[{}]: {} cannot be disabled.".format(chan, target))
            else:
                disabledcommands = '{} {}'.format(target, disabledcommands)
                database.set(db, 'channels', 'disabled', disabledcommands,
                             'chan', chan)
                notice(u"[{}]: {} has been disabled.".format(chan, target))
    return


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def enable(inp, notice, bot, chan, db):
    """enable [#channel] <commands|all> -- Enables commands for a channel.
    (you can enable multiple commands at once)"""

    disabledcommands = database.get(db, 'channels', 'disabled', 'chan', chan)
    targets = inp.split()
    if 'all' in targets or '*' in targets:
        database.set(db, 'channels', 'disabled', '', 'chan', chan)
        notice(u"[{}]: All commands are now enabled.".format(chan))
    else:
        for target in targets:
            if disabledcommands and target in disabledcommands:
                disabledcommands = disabledcommands.split(" ")
                for commands in disabledcommands:
                    if target == commands:
                        disabledcommands = " ".join(disabledcommands)
                        disabledcommands = " ".join(
                            disabledcommands.replace(target,
                                                     '').strip().split())
                        database.set(db, 'channels', 'disabled',
                                     disabledcommands, 'chan', chan)
                        notice(u"[{}]: {} is now enabled.".format(
                            chan, target))
                    else:
                        pass
            else:
                if target in " ".join(bot.config["disabled_commands"]):
                    notice(u"[{}]: {} is globally disabled. Use .genable {} to enable."
                           .format(chan, target, target))
                else:
                    notice(u"[{}]: {} is not disabled.".format(chan, target))
    return


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def disablehash(inp, notice, bot, chan, db):
    """disablehash [#channel] <hashtah> -- Disables hashtah for a channel.
    (you can disable multiple hastags at once, don't put # before the hashtag)"""

    disabledhashes = database.get(db, 'channels', 'disabledhashes', 'chan',
                                  chan)
    targets = inp.split()
    for target in targets:
        if disabledhashes and target in disabledhashes:
            notice(u"[{}]: {} is already disabled.".format(chan, target))
        else:
            if 'disable' in target or 'enable' in target:
                notice(u"[{}]: {} cannot be disabled.".format(chan, target))
            else:
                disabledhashes = '{} {}'.format(target, disabledhashes)
                database.set(db, 'channels', 'disabledhashes', disabledhashes,
                             'chan', chan)
                notice(u"[{}]: {} has been disabled.".format(chan, target))
    return


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def disabledhashes(inp, notice, bot, chan, db):
    """disabledhashes [#channel] -- Lists disabled hashtags."""
    disabledhashes = database.get(db, 'channels', 'disabledhashes', 'chan',
                                  chan)
    if disabledhashes:
        notice(u"[{}]: Disabled hashtags: {}".format(chan, disabledhashes))
    else:
        notice(u"[{}]: No hashtags are currently disabled.".format(chan))
    return


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def enablehash(inp, notice, bot, chan, db):
    """enablehash [#channel] <hashtag|all> -- Enables hashtags for a channel.
    (you can enable multiple hashtags at once, don't put # before the hashtag)"""

    disabledhashes = database.get(db, 'channels', 'disabledhashes', 'chan',
                                  chan)
    targets = inp.split()
    if 'all' in targets or '*' in targets:
        database.set(db, 'channels', 'disabledhashes', '', 'chan', chan)
        notice(u"[{}]: All commands are now enabled.".format(chan))
    else:
        for target in targets:
            if disabledhashes and target in disabledhashes:
                disabledhashes = " ".join(
                    disabledhashes.replace(target, '').strip().split())
                database.set(db, 'channels', 'disabledhashes', disabledhashes,
                             'chan', chan)
                notice(u"[{}]: {} is now enabled.".format(chan, target))
            else:
                notice(u"[{}]: {} is not disabled.".format(chan, target))
    return


########################
### Flood Protection ###


@hook.command(autohelp=False)
def showfloods(inp, chan, notice, db):
    """showfloods [channel] -- Shows flood settings."""

    flood = database.get(db, 'channels', 'flood', 'chan', chan)
    if flood:
        notice(u"[{}]: Flood: {} messages in {} seconds".format(
            chan,
            flood.split()[0],
            flood.split()[1]))
    else:
        notice(u"[{}]: Flood protection is disabled.".format(chan))

    cmdflood = database.get(db, 'channels', 'cmdflood', 'chan', chan)
    if cmdflood:
        notice(u"[{}]: Command Flood: {} commands in {} seconds".format(
            chan,
            cmdflood.split()[0],
            cmdflood.split()[1]))
    else:
        notice(u"[{}]: Command Flood protection is disabled.".format(chan))
    return


@hook.command(channeladminonly=True, autohelp=False)
def flood(inp, chan, notice, db):
    """flood [channel] <number> <duration> | disable -- Enables flood protection for a channel.
    ex: .flood 3 30 -- Allows 3 messages in 30 seconds, set disable to disable"""

    if len(inp) == 0:
        floods = database.get(db, 'channels', 'flood', 'chan', chan)
        if floods:
            notice(u"[{}]: Flood: {} messages in {} seconds".format(
                chan,
                floods.split()[0],
                floods.split()[1]))
        else:
            notice(u"[{}]: Flood is disabled.".format(chan))
            notice(flood.__doc__)
    elif "disable" in inp:
        database.set(db, 'channels', 'flood', None, 'chan', chan)
        notice(u"[{}]: Flood Protection Disabled.".format(chan))
    else:
        flood_num = inp.split()[0]
        flood_duration = inp.split()[1]
        floods = '{} {}'.format(flood_num, flood_duration)
        database.set(db, 'channels', 'flood', floods, 'chan', chan)
        notice(u"[{}]: Flood Protection limited to {} messages in {} seconds."
               .format(chan, flood_num, flood_duration))
    return


@hook.command(channeladminonly=True, autohelp=False)
def cmdflood(inp, chan, notice, db):
    """cmdflood [channel] <number> <duration> | disable -- Enables commandflood protection for a channel.
    ex: .cmdflood 3 30 -- Allows 3 commands in 30 seconds, set disable to disable"""

    if len(inp) == 0:
        floods = database.get(db, 'channels', 'cmdflood', 'chan', chan)
        if floods:
            notice(u"[{}]: Command Flood: {} commands in {} seconds".format(
                chan,
                floods.split()[0],
                floods.split()[1]))
        else:
            notice(u"[{}]: CMD Flood is disabled.".format(chan))
            notice(cmdflood.__doc__)
    elif "disable" in inp:
        database.set(db, 'channels', 'cmdflood', None, 'chan', chan)
        notice(u"[{}]: Command Flood Protection Disabled.".format(chan))
    else:
        flood_num = inp.split()[0]
        flood_duration = inp.split()[1]
        floods = '{} {}'.format(flood_num, flood_duration)
        database.set(db, 'channels', 'cmdflood', floods, 'chan', chan)
        notice(u"[{}]: Command Flood Protection limited to {} commands in {} seconds."
               .format(chan, flood_num, flood_duration))
    return


################
### Badwords ###


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def badwords(inp, notice, bot, chan, db):
    """disabled [#channel] -- Lists disabled commands/."""

    if len(inp) == 0 or 'list' in inp:
        badwordlist = database.get(db, 'channels', 'badwords', 'chan', chan)
        if badwordlist:
            notice(u"[{}]: Bad words: {}".format(chan, badwordlist))
        else:
            notice(u"[{}]: No bad words in list.".format(chan))
            notice(badwords.__doc__)
    elif 'add' or 'del' in inp:
        command = inp.split(' ')[0].strip()
        inp = inp.replace(command, '').strip()
        badwordlist = database.get(db, 'channels', 'badwords', 'chan', chan)
        targets = inp.split()
        if 'add' in command:
            for target in targets:
                if badwordlist and target in badwordlist:
                    notice(u"[{}]: {} is already a bad word.".format(
                        chan, target))
                else:
                    if len(target) < 3:
                        notice(u"[{}]: badwords must be longer than 3 characters. ({})"
                               .format(chan, target))
                    else:
                        badwordlist = '{} {}'.format(target, badwordlist)
                        database.set(db, 'channels', 'badwords', badwordlist,
                                     'chan', chan)
                        notice(u"[{}]: {} has been added to the bad word list."
                               .format(chan, target))
        elif 'del' in command:
            if 'all' in targets or '*' in targets:
                database.set(db, 'channels', 'badwords', '', 'chan', chan)
                notice(u"[{}]: All bad words have been removed.".format(chan))
            else:
                for target in targets:
                    if badwordlist and target in badwordlist:
                        badwordlist = " ".join(
                            badwordlist.replace(target, '').strip().split())
                        database.set(db, 'channels', 'badwords', badwordlist,
                                     'chan', chan)
                        notice(u"[{}]: {} is no longer a bad word.".format(
                            chan, target))
                    else:
                        notice(u"[{}]: {} is not a bad word.".format(
                            chan, target))
    else:
        notice(badwords.__doc__)

    return


############
### Trim ###


@hook.command(channeladminonly=True, autohelp=False)
def trim(inp, chan, notice, db):
    """trim [channel] <length|disable> -- Sets trim length for parsers.
    ex: .trim 150 -- Returns the first 150 characters of a parsed url"""

    if len(inp) == 0:
        trimlength = database.get(db, 'channels', 'trimlength', 'chan', chan)
        if trimlength:
            notice(u"[{}]: Trim output set to {} characters.".format(
                chan, trimlength))
        else:
            notice(u"[{}]: Trim is disabled.".format(chan))
            notice(trim.__doc__)
    elif "disable" in inp or "0 " in inp:
        database.set(db, 'channels', 'trimlength', None, 'chan', chan)
        notice(u"[{}]: Trim Disabled.".format(chan))
    else:
        trimlength = inp.strip()
        database.set(db, 'channels', 'trimlength', trimlength, 'chan', chan)
        notice(u"[{}]: Trim output set to {} characters.".format(
            chan, trimlength))
    return


#####################
### Channel Modes ###


def mode_cmd_channel(mode, text, inp, chan, conn, notice):
    """ generic mode setting function without a target"""
    channels = inp.split(' ')
    for channel in channels:
        if not channel: channel = chan
        notice(u"Attempting to {} {}...".format(text, channel))
        conn.send(u"MODE {} {}".format(channel, mode))


@hook.command(permissions=["op_topic", "op"], channeladminonly=True)
def topic(inp, conn, chan):
    """topic [channel] <topic> -- Change the topic of a channel."""
    split = inp.split(" ")
    message = " ".join(split)
    conn.send(u"TOPIC {} :{}".format(chan, message))


@hook.command(
    permissions=["op_mute", "op"], channeladminonly=True, autohelp=False)
def mute(inp, conn, chan, notice):
    """mute [channel] -- Makes the bot mute a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_channel("+m", "mute", inp, chan, conn, notice)


@hook.command(
    permissions=["op_mute", "op"], channeladminonly=True, autohelp=False)
def unmute(inp, conn, chan, notice):
    """mute [channel] -- Makes the bot mute a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_channel("-m", "unmute", inp, chan, conn, notice)


@hook.command("stfu", adminonly=True)
@hook.command("silence", adminonly=True)
@hook.command(adminonly=True)
def shutup(inp, conn, chan, notice):
    "shutup [channel] <user> -- Shuts the user up. "

    users = inp.split(" ")

    if inp[0][0] == "#":
        chan = inp.split(" ")[0]
        users = inp.split(" ")[1:]

    for user in users:
        out = u"MODE %s +m-voh %s %s %s" % (chan, user, user, user)
        conn.send(out)
        notice(u"Shut up %s from %s..." % (user, chan))


@hook.command(adminonly=True)
def speak(inp, conn, chan, notice):
    "speak [channel] <user> -- Shuts the user up. "

    users = inp.split(" ")

    if inp[0][0] == "#":
        chan = inp.split(" ")[0]
        users = inp.split(" ")[1:]

    for user in users:
        out = u"MODE %s -m" % (chan)
        conn.send(out)
        notice(u"hey %s you can speak in %s again" % (user, chan))


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def lock(inp, conn, chan, notice):
    """lock [channel] -- Makes the bot lock a channel.
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_channel("+i", "lock", inp, chan, conn, notice)


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def unlock(inp, conn, chan, notice):
    """unlock [channel] -- Makes the bot unlock a channel..
    If [channel] is blank the bot will mute
    the channel the command was used in."""
    mode_cmd_channel("-i", "unlock", inp, chan, conn, notice)


##################
### User Modes ###


def mode_cmd(mode, text, inp, chan, conn, notice):
    """ generic mode setting function """
    if len(inp) < 2: inp = conn.nick
    targets = inp.split(" ")
    for target in targets:
        if notice is None:
            conn.send(u"MODE {} {} {}".format(chan, mode, target))
            pass
        else:
            notice(u"Attempting to {} {} in {}...".format(text, target, chan))
            conn.send(u"MODE {} {} {}".format(chan, mode, target))
    return


# @hook.event('*')
# def christisthegay(inp, chan=None, conn=None, notice=None, nick=None, reply=None):
#     if nick == 'Christistheway':
#         reply('Christistheway: proof')


@hook.command(
    permissions=['op_lock', 'op'], channeladminonly=True, autohelp=False)
def bans(inp, notice, bot, chan, db):
    """bans -- Lists bans on channel."""
    bans = database.get(db, 'channels', 'bans', 'chan', chan)
    if bans: notice(u"[{}]: Bans are: {}".format(chan, bans))
    else: notice(u"[{}]: No nicks/hosts are in the banlist.".format(chan))
    return


@hook.command('kb', permissions=["op_ban", "op"], channeladminonly=True)
@hook.command(permissions=["op_ban", "op"], channeladminonly=True)
def ban(inp, conn, chan, notice, db, nick, bot):
    """ban [channel] <user> [reason] [timer] -- Makes the bot ban <user> in [channel].
    If [channel] is blank the bot will ban <user> in
    the channel the command was used in."""
    mode = "+b"
    reason = "#rekt"
    # inp,chan = get_chan(inp,chan)
    split = inp.split(" ")
    inp_nick = split[0]

    if conn.nick in inp_nick or bot.config['owner'] == inp_nick:
        target = nick
        reason = "Your attitude is not conducive to the desired environment"
        conn.send(u"KICK {} {} :{}".format(chan, target, reason))
        return

    if len(split) > 1: reason = " ".join(split[1:])

    if not '@' in inp_nick: target = user.get_hostmask(inp_nick, db)
    else: target = inp_nick

    if '@' in target and not '!' in target: target = '*!*{}'.format(target)
    timer = scheduler.check_for_timers(inp, 'ban')
    if timer > 0:
        reason = "{} Come back in {} seconds!!!".format(reason, timer)
    notice(u"Attempting to ban {} in {}...".format(target, chan))
    conn.send(u"MODE {} {} {}".format(chan, mode, target))
    conn.send(u"KICK {} {} :{}".format(chan, inp_nick, reason))

    if timer > 0:
        notice(u"{} will be unbanned in {} seconds".format(target, timer))
        scheduler.schedule(timer, 1, "MODE {} -b {}".format(chan, target),
                           conn)
        #scheduler.schedule(timer, 2, "PRIVMSG ChanServ :unban {} {}".format(channel, nick), conn)
    else:
        banlist = database.get(db, 'channels', 'bans', 'chan', chan)
        banlist = '{} {}'.format(target, banlist).replace('False', '').strip()
        database.set(db, 'channels', 'bans', banlist, 'chan', chan)
    return


@hook.command('ub', permissions=["op_ban", "op"], channeladminonly=True)
@hook.command(permissions=["op_ban", "op"], channeladminonly=True)
def unban(inp, conn, chan, notice, db):
    """unban [channel] <user> -- Makes the bot unban <user> in [channel].
    If [channel] is blank the bot will unban <user> in
    the channel the command was used in."""
    #mode_cmd("-b", "unban", inp, chan, conn, notice)
    # inp,chan = get_chan(inp,chan)
    split = inp.split(" ")
    nick = split[0]
    if not '@' in nick: target = user.get_hostmask(nick, db)
    else: target = nick
    if '@' in target and not '!' in target: target = '*!*{}'.format(target)
    elif '*' in inp or 'all' in inp:
        notice(u"[{}]: Everyone unbanned".format(chan))
        database.set(db, 'channels', 'bans', '', 'chan', chan)
        return
    notice(u"Attempting to unban {} in {}...".format(target, chan))
    conn.send(u"MODE {} -b {}".format(chan, target))
    banlist = database.get(db, 'channels', 'bans', 'chan', chan)
    banlist = " ".join(banlist.replace(target, '').strip().split())
    database.set(db, 'channels', 'bans', banlist, 'chan', chan)
    return


@hook.command('k', channeladminonly=True)
@hook.command('kal', channeladminonly=True)
@hook.command(permissions=["op_kick", "op"], channeladminonly=True)
def kick(inp, chan, conn, notice, nick, bot):
    """kick [channel] <user> [reason] -- Makes the bot kick <user> in [channel]
    If [channel] is blank the bot will kick the <user> in
    the channel the command was used in."""
    reason = "bye bye"
    # inp,chan = get_chan(inp,chan)
    split = inp.split()
    target = split[0]
    if len(split) > 1: reason = " ".join(split[1:])

    if conn.nick in target or bot.config['owner'] == target:
        target = nick
        reason = "Your attitude is not conducive to the desired environment"

    notice(u"Attempting to kick {} from {}...".format(target, chan))
    conn.send(u"KICK {} {} :{}".format(chan, target, reason))
    return


@hook.command(
    "up", permissions=["op_op", "op"], channeladminonly=True, autohelp=False)
@hook.command(permissions=["op_op", "op"], channeladminonly=True)
def op(inp, conn, chan, notice, nick):
    """op [channel] <user> -- Makes the bot op <user> in [channel].
    If [channel] is blank the bot will op <user> in
    the channel the command was used in."""
    if not inp: inp = nick
    mode_cmd("+o", "op", inp, chan, conn, notice)
    return


@hook.command(
    "down",
    permissions=["op_op", "op"],
    channeladminonly=True,
    autohelp=False)
@hook.command(permissions=["op_op", "op"], channeladminonly=True)
def deop(inp, conn, chan, notice, nick):
    """deop [channel] <user> -- Makes the bot deop <user> in [channel].
    If [channel] is blank the bot will deop <user> in
    the channel the command was used in."""
    if not inp: inp = nick
    mode_cmd("-o", "deop", inp, chan, conn, notice)
    return


@hook.command(
    permissions=["op_op", "op"], channeladminonly=True, autohelp=False)
def hop(inp, chan, conn, notice, nick):
    """op [channel] <user> -- Makes the bot op <user> in [channel].
    If [channel] is blank the bot will op <user> in
    the channel the command was used in."""
    mode_cmd("+h", "hop", inp, chan, conn, notice)
    return


@hook.command(
    permissions=["op_op", "op"], channeladminonly=True, autohelp=False)
def dehop(inp, chan, conn, notice, nick):
    """deop [channel] <user> -- Makes the bot deop <user> in [channel].
    If [channel] is blank the bot will deop <user> in
    the channel the command was used in."""
    mode_cmd("-h", "dehop", inp, chan, conn, notice)
    return


@hook.command(permissions=["op_voice", "op"], channeladminonly=True)
def voice(inp, conn, chan, notice):
    """voice [channel] <user> -- Makes the bot voice <user> in [channel].
    If [channel] is blank the bot will voice <user> in
    the channel the command was used in."""
    mode_cmd("+v", "voice", inp, chan, conn, notice)
    return


@hook.command(permissions=["op_voice", "op"], channeladminonly=True)
def devoice(inp, conn, chan, notice):
    """devoice [channel] <user> -- Makes the bot devoice <user> in [channel].
    If [channel] is blank the bot will devoice <user> in
    the channel the command was used in."""
    mode_cmd("-v", "devoice", inp, chan, conn, notice)
    return


#@hook.command(permissions=["op_voice", "op"], adminonly=True)
@hook.command
def invite(inp, conn, chan, notice):
    """invite [channel] <user> -- Makes the bot invite <user> to [channel].
    If [channel] is blank the bot will invite <user> to
    the channel the command was used in."""
    users = inp.split()
    throttle = 0

    def nestedinvite(user, throttle, sleeptime, users):
        conn.send(u"INVITE {} {}".format(user, chan))
        notice(u"Inviting {} to {}...".format(user, chan))
        sleep(sleeptime)
        users.pop(users.index(user))
        throttle += 1
        return users, throttle

    for user in users:
        # slows down legit invites but better than getting uguu kicked
        # still possible to get uguu kicked but much harder
        if throttle <= 10:
            sleeptime = old_div(len(users), 3)
            # just an extra fuck you to people who do huge invites
            if len(users) >= 20:
                sleeptime += len(users)
            users, throttle = nestedinvite(user, throttle, sleeptime, users)
        else:
            sleep(10)
            throttle = 0
            nestedinvite(users, throttle)


# @hook.command(permissions=["op_quiet", "op"], channeladminonly=True)
# def quiet(inp, conn, chan, notice):
#     """quiet [channel] <user> -- Makes the bot quiet <user> in [channel].
#     If [channel] is blank the bot will quiet <user> in
#     the channel the command was used in."""
#     mode_cmd("+q", "quiet", inp, chan, conn, notice)
#     return

# @hook.command(permissions=["op_quiet", "op"], channeladminonly=True)
# def unquiet(inp, conn, chan, notice):
#     """unquiet [channel] <user> -- Makes the bot unquiet <user> in [channel].
#     If [channel] is blank the bot will unquiet <user> in
#     the channel the command was used in."""
#     mode_cmd("-q", "unquiet", inp, chan, conn, notice)
#     return


@hook.command(permissions=["op_rem", "op"], channeladminonly=True)
def remove(inp, chan, conn):
    """remove [channel] <user> [message] -- Force a user to part from a channel."""
    print(inp)
    message = inp
    conn.send(u"REMOVE {} :{}".format(chan, message))
    return


@hook.command(adminonly=True)
def testdamnit(inp, bot, conn):
    channellist = bot.config["connections"][conn.name]["channels"]
    print(channellist)
    channellist2 = list(set(channellist))
    print(channellist2)
    #for target in targets.split(" "):
    #    if not target.startswith("#"):
    #        target = "#{}".format(target)
    #    notice(u"Attempting to leave {}...".format(target))
    #    conn.part(target)
    #channellist.remove(inp.lower().strip())
    #print channellist
    #json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
