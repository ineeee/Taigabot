import json
import re
import sys
import time

from util import database, hook, user
from utilities.services import paste


@hook.command(autohelp=False, adminonly=True)
def gadmins(inp, notice, bot):
    """gadmins -- Lists bot's global admins."""
    if bot.config["admins"]:
        notice(u"Admins are: %s." % ", ".join(bot.config["admins"]))
    else:
        notice(u"There are no users with global admin powers.")
    return


@hook.command(adminonly=True)
def gadmin(inp, notice, bot, config, db):
    """gadmin <add|del> <nick|host> -- Make <nick|host> an global admin (you can delete multiple admins at once)"""
    inp = inp.lower()
    command = inp.split()[0]
    targets = inp.split()[1:]

    if 'add' in command:
        for target in targets:
            target = user.get_hostmask(target, db)
            if target in bot.config["admins"]:
                notice(u"%s is already a global admin." % target)
            else:
                notice(u"%s is now a global admin." % target)
                bot.config["admins"].append(target)
                bot.config["admins"].sort()
                json.dump(
                    bot.config, open('config', 'w'), sort_keys=True, indent=2)
        return
    elif 'del' in command:
        for target in targets:
            target = user.get_hostmask(target, db)
            if target in bot.config["admins"]:
                notice(u"%s is no longer a global admin." % target)
                bot.config["admins"].remove(target)
                bot.config["admins"].sort()
                json.dump(
                    bot.config, open('config', 'w'), sort_keys=True, indent=2)
            else:
                notice(u"%s is not a global admin." % target)
        return


#################################
### GDisable/GEnable Commands ###


@hook.command(permissions=["op_lock", "op"], adminonly=True, autohelp=False)
def gdisabled(inp, notice, bot, chan, db):
    """gdisabled -- Lists globally disabled commands."""
    if bot.config["disabled_commands"]:
        notice(u"Globally disabled commands are: %s." % ", ".join(
            bot.config["disabled_commands"]))
    else:
        notice(u"There are no globally disabled commands.")
    return


@hook.command(permissions=["op_lock", "op"], adminonly=True)
def gdisable(inp, notice, bot, chan, db):
    """gdisable <commands> -- Makes the bot globally disable a command."""
    disabledcommands = bot.config["disabled_commands"]
    targets = inp.split()
    for target in targets:
        if "gdisable" in target or "genable" in target or "core_admin" in target:
            notice(u"[Global]: {} cannot be disabled.".format(target))
        elif disabledcommands and target in disabledcommands:
            notice(u"[Global]: {} is already disabled.".format(target))
        else:
            bot.config["disabled_commands"].append(target)
            bot.config["disabled_commands"].sort()
            json.dump(
                bot.config, open('config', 'w'), sort_keys=True, indent=2)
            notice(u"[Global]: {} has been disabled.".format(target))
    return


@hook.command(permissions=["op_lock", "op"], adminonly=True)
def genable(inp, notice, bot, chan, db):
    """genable <commands> -- Enables currently globally disabled commands"""
    disabledcommands = bot.config["disabled_commands"]
    targets = inp.split()
    for target in targets:
        if disabledcommands and target in disabledcommands:
            bot.config["disabled_commands"].remove(target)
            bot.config["disabled_commands"].sort()
            json.dump(
                bot.config, open('config', 'w'), sort_keys=True, indent=2)
            notice(u"[Global]: {} has been enabled.".format(target))
        else:
            notice(u"[Global]: {} is not disabled.".format(target))
    return


# if 'all' in targets or '*' in targets:

################################
### Ignore/Unignore Commands ###


@hook.command(permissions=["op_lock", "op"], adminonly=True, autohelp=False)
def gignored(inp, notice, bot, chan, db):
    """gignored [channel] -- Lists ignored channels/nicks/hosts."""
    if bot.config["ignored"]:
        penis = ", ".join(bot.config["ignored"])
        if len(penis) > 100:
            vagina = '\n- '.join(bot.config["ignored"])  # use newlines instead of commas
            link = paste(vagina)
            notice(f'Global ignores are {link}, here are some: {penis}')
        else:
            notice(f'Global ignores are: {penis}')
    else:
        notice(u"There are no global ignores.")
    return


@hook.command(permissions=["op_lock", "op"], adminonly=True, autohelp=False)
def gignore(inp, notice, bot, chan, db):
    """gignore <nick|host> -- Makes the bot ignore nick|host."""
    ignorelist = bot.config["ignored"]
    targets = inp.split()
    for target in targets:
        target = user.get_hostmask(target, db)
        if (user.is_globaladmin(target, db, bot)):
            notice(u"[Global]: {} is an admin and cannot be ignored.".format(
                inp))
        else:
            if ignorelist and target in ignorelist:
                notice(u"[Global]: {} is already ignored.".format(target))
            else:
                bot.config["ignored"].append(target)
                bot.config["ignored"].sort()
                json.dump(
                    bot.config, open('config', 'w'), sort_keys=True, indent=2)
                notice(u"[Global]: {} has been ignored.".format(target))
    return
    #         if ignorelist and target in ignorelist:
    #             notice(u"[{}]: {} is already ignored.".format(chan, target))
    #         else:
    #             ignorelist = '{} {}'.format(target,ignorelist)
    #             database.set(db,'channels','ignored',ignorelist,'chan',chan)

    #             notice(u"[{}]: {} has been ignored.".format(chan,target))
    # return


@hook.command(permissions=["op_lock", "op"], adminonly=True, autohelp=False)
def gunignore(inp, notice, bot, chan, db):
    """gunignore [channel] <nick|host> -- Makes the bot listen to <nick|host>."""
    ignorelist = bot.config["ignored"]
    targets = inp.split()
    for target in targets:
        target = user.get_hostmask(target, db)
        if ignorelist and target in ignorelist:
            bot.config["ignored"].remove(target)
            bot.config["ignored"].sort()
            json.dump(
                bot.config, open('config', 'w'), sort_keys=True, indent=2)
            notice(u"[Global]: {} has been unignored.".format(target))
        else:
            notice(u"[Global]: {} is not ignored.".format(target))
    return


@hook.command(
    "quit", autohelp=False, permissions=["botcontrol"], adminonly=True)
@hook.command(autohelp=False, permissions=["botcontrol"], adminonly=True)
def stop(inp, nick, conn):
    """stop [reason] -- Kills the bot with [reason] as its quit message."""
    if inp:
        conn.cmd("QUIT", ["Killed by {} ({})".format(nick, inp)])
    else:
        conn.cmd("QUIT", ["Killed by {}.".format(nick)])
    time.sleep(5)
    #os.execl("./bot", "bot", "stop")


@hook.command(autohelp=False, permissions=["botcontrol"], adminonly=True)
def restart(inp, nick, bot):
    """restart [reason] -- Restarts the bot with [reason] as its quit message."""
    for botcon in bot.conns:
        if inp:
            bot.conns[botcon].cmd("QUIT", [
                "Restarted by {} ({})".format(nick, inp)
            ])
        else:
            bot.conns[botcon].cmd("QUIT", ["Restarted by {}.".format(nick)])

    sys.exit(0)


@hook.command(autohelp=False, permissions=["botcontrol"], adminonly=True)
def join(inp, conn, notice, bot):
    """join <channel> -- Joins <channel>."""
    if "0,0" in inp: return
    for target in inp.split(" "):
        key = None
        if ":" in target:
            key = target.split(":")[1]
            target = target.split(":")[0]
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice(u"Attempting to join {}...".format(target))
        if key:
            conn.join(target, key)
        else:
            conn.join(target)

        channellist = bot.config["connections"][conn.name]["channels"]
        if not target.lower() in channellist:
            channellist.append(target.lower())
            json.dump(
                bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(autohelp=False, permissions=["botcontrol"], adminonly=True)
def part(inp, conn, chan, notice, bot):
    """part [channel] -- Leaves [channel]. If [channel] is blank, leave the current channel."""
    if inp: targets = inp
    else: targets = chan

    channellist = bot.config["connections"][conn.name]["channels"]

    for target in targets.split(" "):
        if not target.startswith("#"):
            target = "#{}".format(target)
        if target in conn.channels:
            notice(u"Attempting to leave {}...".format(target))
            conn.part(target)
            channellist.remove(target.lower().strip())
            print('Deleted {} from channel list.'.format(target))
        else:
            notice(u"Not in {}!".format(target))

    json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
    return


@hook.command(autohelp=False, permissions=["botcontrol"], adminonly=True)
def cycle(inp, conn, chan, notice):
    """cycle [channel] -- Cycles [channel]. If [channel] is blank, cycle the current channel."""
    if inp:
        target = inp
    else:
        target = chan
    notice(u"Attempting to cycle {}...".format(target))
    conn.part(target)
    conn.join(target)
    return


@hook.command(permissions=["botcontrol"], adminonly=True)
def nick(inp, notice, conn):
    """nick <nick> -- Changes the bots nickname to <nick>."""
    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        notice(u"Invalid username!")
        return
    notice(u"Attempting to change nick to \"{}\"...".format(inp))
    conn.set_nick(inp)
    return


@hook.command(permissions=["botcontrol"], adminonly=True)
def raw(inp, conn, notice):
    """raw <command> -- Sends a RAW IRC command."""
    notice(u"Raw command sent.")
    conn.send(inp)


@hook.command(permissions=["botcontrol"], adminonly=True)
def say(inp, conn, chan):
    """say [channel] <message> -- Say <message> in [channel]. If [channel] is blank, send in current channel."""
    inp = inp.split(" ")
    if inp[0][0] == "#":
        message = " ".join(inp[1:])
        out = u"PRIVMSG {} :{}".format(inp[0], message)
    else:
        message = " ".join(inp[0:])
        out = u"PRIVMSG {} :{}".format(chan, message)
    conn.send(out)


@hook.command(adminonly=True)
def msg(inp, conn, chan, notice):
    """msg <user> <message> -- Sends a Message."""
    user = inp.split()[0]
    message = inp.replace(user, '').strip()
    out = u"PRIVMSG %s :%s" % (user, message)
    conn.send(out)


@hook.command("act", permissions=["botcontrol"], adminonly=True)
@hook.command(permissions=["botcontrol"], adminonly=True)
def me(inp, conn, chan):
    """me [channel] <action> -- Act out <action> in [channel]. If [channel] is blank, use the current channel."""
    inp = inp.split(" ")
    if inp[0][0] == "#":
        message = ""
        for x in inp[1:]:
            message = message + x + " "
        message = message[:-1]
        out = u"PRIVMSG {} :\x01ACTION {}\x01".format(inp[0], message)
    else:
        message = ""
        for x in inp[0:]:
            message = message + x + " "
        message = message[:-1]
        out = u"PRIVMSG {} :\x01ACTION {}\x01".format(chan, message)
    conn.send(out)


@hook.command(adminonly=True)
def set(inp, conn, chan, db, notice):  # holy fucking shit this function is ass
    """set <field> <nick> <value> -- Admin override for setting database values. Example: set lastfm infinity spookieboogie"""

    inpsplit = inp.split(" ")

    if len(inpsplit) == 2:
        field = inp.split(" ")[0].strip()
        value = inp.split(" ")[1].strip()

        if 'voteban' in field or \
            'votekick' in field:
            database.set(db, 'channels', field, value, 'chan', chan)
            notice(u"Set {} to {}.".format(field, value))
            return
    elif len(inpsplit) >= 3:
        field = inp.split(" ")[0].strip()
        nick = inp.split(" ")[1].strip()
        # value = inp.replace(field,'').replace(nick,'').strip()
        value = inp.strip()
        vsplit = value.split()
        if len(vsplit[1:]) >= 2:
            value = ' '.join(vsplit[2:])
        else:
            value = ''.join(vsplit[2:])
        if field and nick and value:
            if 'del' in value or 'none' in value: value = ''
            if 'location' in field or \
                'fines' in field or\
                'lastfm' in field or  \
                'desktop' in field or \
                'battlestation' in field or\
                'birthday' in field or\
                'waifu' in field or\
                'imouto' in field or\
                'husbando' in field or\
                'daughteru' in field or\
                'horoscope' in field or\
                'homescreen' in field or\
                'myanime' in field or\
                'mymanga' in field or\
                'selfie' in field or\
                'steam' in field or\
                'greeting' in field or\
                'seen' in field or\
                'socialmedias' in field or\
                'woeid' in field or\
                'snapchat' in field:
                #if type(value) is list: value = value[0]
                if value.lower() == 'none':
                    database.set(db, 'users', field, '', 'nick', nick)
                else:
                    database.set(db, 'users', field, value, 'nick', nick)
                notice(u"Set {} for {} to {}.".format(field, nick, value))
                return

    notice(u"Could not set {}.".format(field))
    return


@hook.command(autohelp=False, adminonly=True)
def db(inp, db, notice, chan):
    """db <update|init> -- Init or update the database."""
    if 'update' in inp:
        database.update(db)
        notice('[{}]: Updated databases.'.format(chan))
    elif 'init' in inp:
        database.init(db)
        notice('[{}]: Initiated databases.'.format(chan))
