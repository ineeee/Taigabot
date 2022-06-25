from util import hook


@hook.command(adminonly=True, autohelp=False)
def test_docstrings(inp, bot):
    """test: make sure all commands have a docstring. docstrings are used for help commands"""

    # types of failures:
    # - missing docstring: the decorated function doesn't have any documentation at all
    # - multiline docstring: the function has a multiline string and it can't be sent over irc

    failed = []

    for command, (func, args) in bot.commands.items():
        if func.__doc__ is None:
            failed.append(('missing', command, f'{func._filename}:{func.__code__.co_firstlineno}'))
        elif '\n' in func.__doc__:
            failed.append(('multiline', command, f'{func._filename}:{func.__code__.co_firstlineno}'))

    if len(failed) == 0:
        return 'all commands passed the test'

    print('commands that failed the docstring test:')
    for (reason, command, source) in failed:
        print(f'- {reason}: {command} defined in {source}')

    return f'there are {len(failed)} commands that did not pass the test'
