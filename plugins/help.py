import re

from util import hook, user
from utilities import services


@hook.command(autohelp=False)
def commands(inp, say, notice, input, conn, bot, db):
    """commands [command] -- Gives a list of available commands, or help for [command]"""
    funcs = {}
    disabled = bot.config.get('disabled_plugins', [])
    disabled_comm = bot.config.get('disabled_commands', [])

    user_is_gadmin = user.is_globaladmin(input.mask, input.chan, bot)
    user_is_admin = user.is_admin(input.mask, input.chan, db, bot)

    for command, (func, args) in bot.commands.items():
        fn = re.match(r'^plugins.(.+).py$', func._filename)

        if fn.group(1).lower() not in disabled and command not in disabled_comm:  # hide disabled plugins and commands
            if args.get('channeladminonly', False) and not user_is_admin:
                continue
            if args.get('adminonly', False) and not user_is_gadmin:
                continue
            if func.__doc__ is not None:
                if func in funcs:
                    if len(funcs[func]) < len(command):
                        funcs[func] = command
                else:
                    funcs[func] = command

    commands = dict((value, key) for key, value in funcs.items())

    if not inp:
        # only use the command names
        commands = list(commands.keys())
        commands.sort()

        if len(', '.join(commands)) < 320:
            # if the output is short, send it as a message
            notice('Commands you have access to ({}): {}'.format(len(commands), ', '.join(commands)))
        else:
            # otherwise paste it to a website
            output = f'Commands you have access to ({len(commands)}):\n'
            output += ', '.join(commands) + '\n\n'
            output += 'For help with a command, do {}help <command>'.format(conn.conf['command_prefix'])

            link = services.paste(output, 'Available commands')
            notice(f'List of commands you have access to ({len(commands)}): {link}')

    elif inp in commands:
        notice("{}{}".format(conn.conf["command_prefix"], commands[inp].__doc__))

    return


@hook.command('command', autohelp=False)
@hook.command(autohelp=False)
def help(inp, say, notice, input, conn, bot, db):
    """help [command] -- show help for [command]"""
    if not inp:
        pref = conn.conf['command_prefix']
        say(f'For help see \x02{pref}commands\x02 or \x02{pref}help <command>\x02')
    else:
        commands(inp, say, notice, input, conn, bot, db)

    return


# @hook.command(autohelp=False)
# def export(inp, bot):
#     #print bot.commands #.iteritems()
#     helptext = ''
#     for command, (func, args) in bot.commands.iteritems():
#         #print command.__doc__
#         helptext = helptext + u'{}\n'.format(func.__doc__).encode('utf-8')

#         #print '{} {} {}'.format(command,func,args)

#     with open('plugins/data/help.txt', 'a') as file:
#         file.write(u'{}\n'.format(helptext).encode('utf-8'))
#     file.close()
#     print helptext
