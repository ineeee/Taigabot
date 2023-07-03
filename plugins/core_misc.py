from __future__ import division
from past.utils import old_div
import json
import re
import socket
import time
from util import database, hook, user

socket.setdefaulttimeout(10)
nick_re = re.compile(":(.+?)!")


# Identify to NickServ (or other service)
@hook.event('004')
def onjoin(paraml, conn=None, bot=None):
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        if nickserv_password in bot.config['censored_strings']:
            bot.config['censored_strings'].remove(nickserv_password)
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        bot.config['censored_strings'].append(nickserv_password)
        time.sleep(2)

    # Set bot modes
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    # Join config-defined channels
    try:
        if len(conn.channels) > 30:
            channels1 = conn.channels[:old_div(len(conn.channels), 2)]
            conn.join(','.join(channels1))
            channels2 = conn.channels[old_div(len(conn.channels), 2):]
            conn.join(','.join(channels2))
            time.sleep(1)
            print(conn.channels)
            print(channels1)
            print(len(channels1))
            print(channels2)
            print(len(channels2))
        else:
            conn.join(','.join(conn.channels))
        print(len(conn.channels))
    except:
        for channel in conn.channels:
            conn.join(channel)
            time.sleep(1)

    print("Bot ready.")


# Auto-join on Invite (Configurable, defaults to True)
@hook.event('INVITE')
def invite(paraml, conn=None, bot=None):
    invite_join = conn.conf.get('invite_join', True)
    if invite_join:
        conn.join(paraml[-1])
        channellist = bot.config["connections"][conn.name]["channels"]
        channellist.append(paraml[-1].lower())
        json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)


@hook.event("KICK")
def onkick(paraml, conn=None, chan=None, bot=None):
    # if the bot has been kicked, remove from the channel list
    # conn.channels.remove(chan)
    if paraml[1] == conn.nick:
        auto_rejoin = conn.conf.get('auto_rejoin', False)
        if auto_rejoin:
            time.sleep(5)
            conn.join(paraml[0])
        else:
            channellist = bot.config["connections"][conn.name]["channels"]
            channellist.remove(paraml[0])
            json.dump(
                bot.config, open('config', 'w'), sort_keys=True, indent=2)


@hook.event("JOIN")
def onjoined(inp, input=None, conn=None, chan=None, raw=None, db=None):
    database.set(
        db, 'users', 'mask',
        input.mask.replace('~', ''), 'nick', input.nick.lower())

    mask = user.format_hostmask(input.mask)
    disabled_commands = database.get(db, 'channels', 'disabled', 'chan', chan)
    if not disabled_commands:
        disabled_commands = ""

    if 'banlist' not in disabled_commands:
        # check if bans
        banlist = database.get(db, 'channels', 'bans', 'chan', chan)
        if banlist and mask in banlist:
            conn.send(f"MODE {input.chan} +b *{mask}")
            conn.send(f"KICK {input.chan} {input.nick} :I dont think so Tim.")

    if 'greeting' not in disabled_commands:
        # send greeting
        greeting = database.get(db, 'users', 'greeting', 'nick', input.nick)
        if greeting:
            return '\x02\x02{}'.format(greeting)


@hook.event("PART")
def onpart(inp, input=None, conn=None, chan=None, raw=None, db=None):
    database.set(
        db, 'users', 'mask',
        input.mask.lower().replace('~', ''), 'nick', input.nick.lower())


@hook.event("NICK")
def onnick(paraml, conn=None, raw=None):
    old_nick = nick_re.search(raw).group(1)
    new_nick = str(paraml[0])
    if old_nick == conn.nick:
        conn.nick = new_nick
        print("Bot nick changed from '{}' to '{}'.".format(old_nick, new_nick))


@hook.event("MODE")
def onmode(
        paraml, input=None, conn=None, raw=None, chan=None, db=None, bot=None):
    if '#defect' in chan.lower():
        if not user.is_admin(input.mask, chan, db, bot):
            fixed_modes = []
            params = []
            param_num = 2
            accepted_modes = 'vhoaql'
            doesnt_require_param = 'cntspmiBCMNRSzO'
            requires_param = 'klvhoaqbeI'
            modes = list(str(paraml[1]))
            for mode in modes:
                if mode == '+':
                    fixed_modes.append(mode.replace('+', '-'))
                elif mode == '-':
                    fixed_modes.append(mode.replace('-', '+'))
                else:
                    if mode not in accepted_modes:
                        if mode in doesnt_require_param:
                            fixed_modes.append(mode)
                        elif mode in requires_param:
                            fixed_modes.append(mode)
                            if mode not in 'kl':
                                params.append(paraml[param_num])
                            param_num += 1
                    else:
                        if mode in requires_param:
                            param_num += 1

            if len(fixed_modes) > 1:
                conn.send(
                    u'MODE {} {} {}'.format(
                        chan, ''.join(fixed_modes), ' '.join(params)))


@hook.singlethread
@hook.event('004')
def keep_alive(paraml, conn=None):
    keepalive = conn.conf.get('keep_alive', False)
    if keepalive:
        while True:
            conn.cmd('PING', [conn.nick])
            time.sleep(60)
