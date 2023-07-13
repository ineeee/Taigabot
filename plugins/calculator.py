# fend calculator plugin by ine
# requires "fend" calculator installed in the system:
# https://printfn.github.io/fend/
import subprocess
from util import hook

try:
    subprocess.run(['/usr/bin/fend', '1+1'])
except FileNotFoundError:
    print('ERROR in calculator.py: the system doesnt have "fend" installed')
    raise  # intentionally interrupt plugin loading


@hook.command('calc')
@hook.command()
def c(inp, nick):
    """c <equation> -- calculate something. supported: () ! ^ ** + - and or xor to in sqrt sin cos tan abs log exp"""
    process = subprocess.run(['/usr/bin/fend', '--', inp], stdout=subprocess.PIPE)  # should probably limit input length

    # return if the parser didn't like the input
    if process.returncode != 0:
        return f'{nick}: error while running the calculator or while parsing your input'

    result = process.stdout.decode('utf-8')

    # replace newlines with spaces
    if '\n' in result:
        result = result.replace('\n', '    ')

    # trim max length
    if len(result) > 200:
        result = result[:200] + '...'

    return f'{nick}: {result}'
