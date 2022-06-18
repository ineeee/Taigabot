import collections
import hashlib
import re
import time

from util import hook, text

# variables

colors = collections.OrderedDict(
    [
        ('red', '\x0304'),
        ('ornage', '\x0307'),
        ('yellow', '\x0308'),
        ('green', '\x0309'),
        ('cyan', '\x0303'),
        ('ltblue', '\x0310'),
        ('rylblue', '\x0312'),
        ('blue', '\x0302'),
        ('magenta', '\x0306'),
        ('pink', '\x0313'),
        ('maroon', '\x0305'),
    ]
)

# helper functions

strip_re = re.compile(r'(\x03|\x02|\x1f)(?:,?\d{1,2}(?:,\d{1,2})?)?', re.UNICODE)


def strip(text):
    return strip_re.sub('', text)


# basic text tools


## TODO: make this capitalize sentences correctly
@hook.command("capitalise")
@hook.command
def capitalize(inp):
    """capitalize <string> -- Capitalizes <string>."""
    return inp.capitalize()


@hook.command
def upper(inp):
    """upper <string> -- Convert string to uppercase."""
    return inp.upper()


@hook.command
def lower(inp):
    """lower <string> -- Convert string to lowercase."""
    return inp.lower()


@hook.command
def titlecase(inp):
    """title <string> -- Convert string to title case."""
    return inp.title()


@hook.command
def swapcase(inp):
    """swapcase <string> -- Swaps the capitalization of <string>."""
    return inp.swapcase()


# # encoding
# @hook.command
# def rot13(inp):
#     """rot13 <string> -- Encode <string> with rot13."""
#     return inp.encode('rot13')


# @hook.command
# def base64(inp):
#     """base64 <string> -- Encode <string> with base64."""
#     return inp.encode('base64')


# @hook.command
# def unbase64(inp):
#     """unbase64 <string> -- Decode <string> with base64."""
#     return inp.decode('base64')


# @hook.command
# def checkbase64(inp):
#     try:
#         decoded = inp.decode('base64')
#         recoded = decoded.encode('base64').strip()
#         is_base64 = recoded == inp
#     except:
#         is_base64 = False

#     if is_base64:
#         return '"{}" is base64 encoded'.format(recoded)
#     else:
#         return '"{}" is not base64 encoded'.format(inp)


# @hook.command
# def unescape(inp):
#     """unescape <string> -- Unescapes <string>."""
#     try:
#         return inp.decode('unicode-escape')
#     except Exception as e:
#         return "Error: {}".format(e)


# @hook.command
# def escape(inp):
#     """escape <string> -- Escapes <string>."""
#     try:
#         return inp.encode('unicode-escape')
#     except Exception as e:
#         return "Error: {}".format(e)


# length
@hook.command
def length(inp):
    """length <string> -- gets the length of <string>"""
    return f'The length of that string is {len(inp)} characters.'


# reverse
@hook.command
def reverse(inp):
    """reverse <string> -- reverses <string>."""
    return inp[::-1]


# hashing
@hook.command
def hash(inp):
    """hash <string> -- Returns hashes of <string>."""
    return ', '.join(x + ': ' + getattr(hashlib, x)(inp.encode('utf-8')).hexdigest() for x in ['md5', 'sha1', 'sha256'])


# novelty
@hook.command
def munge(inp):
    """munge <text> -- Munges up <text>."""
    return text.munge(inp)


# colors - based on code by Reece Selwood - <https://github.com/hitzler/homero>


def make_rainbow(inp):
    inp = str(inp)
    inp = strip(inp)
    col = list(colors.items())
    out = ''
    le = len(colors)
    for i, t in enumerate(inp):
        if t == ' ':
            out += t
        else:
            out += col[i % le][1] + t
    return out


@hook.command("gay")
@hook.command
def rainbow(inp):
    return make_rainbow(inp)


@hook.command
def gaycow(inp, reply):
    reply(make_rainbow(' ' + '_' * (len(inp) + 2)))
    reply(make_rainbow(f'< {inp} >'))
    reply(make_rainbow(' ' + '-' * (len(inp) + 2)))
    reply(make_rainbow('      \\   ^__^'))
    reply(make_rainbow('       \\  (oo)\\_______'))
    reply(make_rainbow('          (__)\\       )\\/\\'))
    time.sleep(1)
    reply(make_rainbow('              ||----w |'))
    reply(make_rainbow('              ||     ||'))


@hook.command
def wrainbow(inp):
    inp = str(inp)
    col = list(colors.items())
    inp = strip(inp).split(' ')
    out = []
    l = len(colors)
    for i, t in enumerate(inp):
        out.append(col[i % l][1] + t)
    return ' '.join(out)


@hook.command('uk')
@hook.command
def usa(inp):
    inp = strip(inp)
    c = [colors['red'], '\x0300', colors['blue']]
    l = len(c)
    out = ''
    for i, t in enumerate(inp):
        out += c[i % l] + t
    return out
