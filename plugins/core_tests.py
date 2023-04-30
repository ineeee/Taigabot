import re
import inspect
import json

from util import hook


@hook.command(adminonly=True, autohelp=False)
def testdocstrings(inp, bot):
    """testdocstrings -- make sure all commands have the docstrings used for help commands"""

    # types of failures:
    # - missing docstring: the decorated function doesn't have any documentation at all
    # - multiline docstring: the function has a multiline string and it can't be sent over irc

    failed = []
    count = 0

    for command, (func, args) in bot.commands.items():
        count += 1

        if func.__doc__ is None:
            failed.append(('missing', command, f'{func.__code__.co_filename}:{func.__code__.co_firstlineno}'))
        elif '\n' in func.__doc__:
            failed.append(('multiline', command, f'{func.__code__.co_filename}:{func.__code__.co_firstlineno}'))
        else:
            regex = r'^([a-z0-9_]+)( <[0-9a-z #@\|\.]+>| \[[0-9a-z #@\|\.]+\])*( -- |: )(.+)$'
            match = re.search(regex, func.__doc__)

            if match is None:
                failed.append(('format', command, f'{func.__code__.co_filename}:{func.__code__.co_firstlineno} {func.__doc__}'))

    if len(failed) == 0:
        return f'all {count} commands passed the test'

    print('commands that failed the docstring test:')
    for (reason, command, source) in failed:
        print(f'- {reason}: {command} defined in {source}')

    return f'[TESTS] there are {len(failed)} commands that did not pass the test, out of {count} total'


@hook.command(adminonly=True)
def testfunctiondefinition(inp, bot):
    """testfunctiondefinition -- ensure commands are not using the old command caller code path"""
    failed = []
    count = 0

    for command, (func, args) in bot.commands.items():
        count += 1
        a = inspect.getfullargspec(func)
        if a.varargs is not None or a.varkw is not None or a.defaults is not None or a.kwonlyargs != []:
            failed.append((command, func.__name__, a))

    if len(failed) == 0:
        return f'all {count} commands passed the test'

    print('commands that failed the function definition test:')
    for (reason, command, source) in failed:
        print(f'- {reason}: {command} defined in {source}')

    return f'[TESTS] there are {len(failed)} commands that did not pass the test, out of {count} total'


@hook.command(adminonly=True)
def exportpluginsjson(inp, bot):
    """exportpluginsjson -- export plugins to plugins.json file"""
    commands = {}
    regexes = {}
    events = {}
    sieves = {}
    count = 0

    pl_commands = bot.plugs.get('command', [])
    pl_events = bot.plugs.get('event', [])
    pl_regex = bot.plugs.get('regex', [])
    pl_sieve = bot.plugs.get('sieve', [])

    # parse commands
    for (func, args) in pl_commands:
        count += 1
        argspec = inspect.getfullargspec(func)

        # uuid = filename: function(arg1, arg2, ...)
        uuid = f'{func.__code__.co_filename}:{func.__code__.co_firstlineno} {func.__name__}()'

        if uuid not in commands:
            commands[uuid] = {
                'function': func.__name__,
                'filename': func.__code__.co_filename,
                'lineno': func.__code__.co_firstlineno,
                'help': func.__doc__,
                'args': list(argspec.args),
                'hook': args,  # TODO check this only grabs the first decorator
                'triggers': [],
            }

        commands[uuid]['triggers'].append(args['name'])

    # parse regexes
    for (func, args) in pl_regex:
        count += 1
        uuid = f'{func.__code__.co_filename}:{func.__code__.co_firstlineno} {func.__name__}()'

        if uuid not in events:
            regexes[uuid] = {
                'function': func.__name__,
                'filename': func.__code__.co_filename,
                'lineno': func.__code__.co_firstlineno,
                'help': func.__doc__,
                'regexes': [],
            }
        else:
            print('warning: duplicated regex decorator??', uuid)

        regexes[uuid]['regexes'].append(args['regex'])

    # parse events
    for (func, args) in pl_events:
        count += 1
        uuid = f'{func.__code__.co_filename}:{func.__code__.co_firstlineno} {func.__name__}()'

        if uuid not in events:
            events[uuid] = {
                'function': func.__name__,
                'filename': func.__code__.co_filename,
                'lineno': func.__code__.co_firstlineno,
                'help': func.__doc__,
                'events': [],
            }
        else:
            print('warning: duplicated event decorator?', uuid)

        for event in args['events']:
            events[uuid]['events'].append(event)

    # parse sieves
    for (func, ) in pl_sieve:
        count += 1
        uuid = f'{func.__code__.co_filename}:{func.__code__.co_firstlineno} {func.__name__}()'

        sieves[uuid] = {
            'function': func.__name__,
            'filename': func.__code__.co_filename,
            'lineno': func.__code__.co_firstlineno
        }

    output = {
        'commands': commands,
        'events': events,
        'regexes': regexes,
        'sieves': sieves,
    }

    file = open('plugins.json', 'w')
    json.dump(output, file, indent=2)
    file.close()

    return f'[EXPORT] dumped {count} functions to plugins.json'
