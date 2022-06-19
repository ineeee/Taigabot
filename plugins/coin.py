from collections.abc import Callable
from util import hook
import random


@hook.command(autohelp=False)
def coin(inp: str, me: Callable):
    """coin [amount] -- Flips [amount] of coins."""

    if inp:
        try:
            amount = int(inp)
        except (ValueError, TypeError):
            return 'Invalid input!'
    else:
        amount = 1

    if amount > 1_000_000:
        return 'are you crazy? i cant hold that many coins'

    if amount == 1:
        me('flips a coin and gets {}.'.format(random.choice(['heads', 'tails'])))
    elif amount == 0:
        me('makes a coin flipping motion with its hands.')
    else:
        heads = int(random.normalvariate(0.5 * amount, (0.75 * amount) ** 0.5))
        tails = amount - heads
        me(f'flips {amount} coins and gets {heads} heads and {tails} tails.')
