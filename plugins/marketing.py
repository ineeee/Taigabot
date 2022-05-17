# bullshite marketing
from util import hook
from random import choice

with open("plugins/data/marketing.txt") as f:
    BULLSHITE = [line.strip() for line in f.readlines() if not line.startswith("//")]

@hook.command(autohelp=False)
def marketing(inp):
	return choice(BULLSHITE)
