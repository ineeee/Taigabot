import re
import inspect
import json

from util import hook


@hook.command(adminonly=True, autohelp=False)
def test_docstrings(inp, bot):
    """test: make sure all commands have a docstring. docstrings are used for help commands"""

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
def test_function_definition(inp, bot):
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
def export_commands_json(inp, bot):
    commands = {}
    count = 0

    print(bot)
    print(', \n'.join("%s: %s\n\n" % item for item in vars(bot).items()))
    return 'uwu'

    for command, (func, args) in bot.commands.items():
        print(command, func._hook)
        count += 1
        argspec = inspect.getfullargspec(func)
        funcargs = ', '.join(argspec.args)

        # uuid = name(arg1, arg2, ...)
        uuid = f'{func.__name__}({funcargs})'

        if uuid not in commands:
            commands[uuid] = {
                'function': func.__name__,
                'filename': func.__code__.co_filename,
                'lineno': func.__code__.co_firstlineno,
                'help': func.__doc__,
                'args': list(argspec.args),
                'triggers': [],
            }

        commands[uuid]['triggers'].append(command)

    file = open('commands.json', 'w')
    json.dump(commands, file, indent=2)
    file.close()

    return f'[EXPORT] dumped {count} commands to commands.json'
