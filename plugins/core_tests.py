import re

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
            failed.append(('missing', command, f'{func._filename}:{func.__code__.co_firstlineno}'))
        elif '\n' in func.__doc__:
            failed.append(('multiline', command, f'{func._filename}:{func.__code__.co_firstlineno}'))
        else:
            regex = r'^([a-z0-9]+)( <[0-9a-z #@|]+>| \[[0-9a-z #@|]+\])*( -- |: )(.+)$'
            match = re.search(regex, func.__doc__)

            if match is None:
                failed.append(('format', command, f'{func._filename}:{func.__code__.co_firstlineno} {func.__doc__}'))

    if len(failed) == 0:
        return f'all {count} commands passed the test'

    print('commands that failed the docstring test:')
    for (reason, command, source) in failed:
        print(f'- {reason}: {command} defined in {source}')

    return f'[TESTS] there are {len(failed)} commands that did not pass the test, out of {count} total'
