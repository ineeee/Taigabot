import random
from util import hook


@hook.command('decide')
@hook.command
def choose(inp):
    """choose <choice1> [choice2] [choice3] -- Randomly picks one of the given choices."""

    if inp == 'eat':
        return 'Yes'

    if inp == 'sleep':
        return 'Never'

    replacewords = {'should', 'could', '?', ' i ', ' you '}

    for word in replacewords:
        inp = inp.replace(word, '')

    if ':' in inp:
        inp = inp.split(':')[1]

    c = inp.split(', ')
    if len(c) == 1:
        c = inp.split(' or ')
        if len(c) == 1:
            c = ['Yes', 'No']

    return random.choice(c).strip()
