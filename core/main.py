import re
import _thread
import traceback
import queue
import inspect
from collections.abc import Callable

_thread.stack_size(1024 * 512)    # reduce vm size


class Input(dict):
    def __init__(self, conn, raw, prefix, command, params, nick, user, host, mask, paraml, msg):

        chan = paraml[0].lower()
        if chan == conn.nick.lower():  # is a PM
            chan = nick

        def say(msg: str):
            conn.msg(chan, msg)

        def reply(msg: str):
            if chan == nick:  # PMs don't need prefixes
                conn.msg(chan, msg)
            else:
                try:
                    conn.msg(chan, re.match(r'\.*(\w+.*)', msg).group(1))  # ??
                except Exception:  # IndexError?
                    conn.msg(chan, msg)

        def me(msg: str):
            conn.msg(chan, f'\x01ACTION {msg}\x01')

        def ctcp(msg: str, ctcp_type: str, target: str = chan):
            """sends an ctcp to the current channel/user or a specific channel/user"""
            conn.ctcp(target, ctcp_type, msg)

        def notice(msg: str):
            conn.cmd('NOTICE', [nick, msg])

        dict.__init__(
            self,
            conn=conn,
            raw=raw,
            prefix=prefix,
            command=command,
            params=params,
            nick=nick,
            user=user,
            host=host,
            mask=mask,
            paraml=paraml,
            msg=msg,
            server=conn.server,
            chan=chan,
            notice=notice,
            say=say,
            reply=reply,
            bot=bot,
            me=me,
            lastparam=paraml[-1])

    # make dict keys accessible as attributes
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def run(func: Callable, input: Input):
    args = func._args

    if 'inp' not in input:
        input.inp = input.paraml

    # ### START: new code ### #
    argspec = inspect.getfullargspec(func)
    real_args = argspec.args

    if real_args:
        successfully_used_new_method = True

        if 'db' in real_args and 'db' not in input:
            input.db = bot.get_db_connection(input.conn)
        if 'input' in real_args:
            input.input = input

        func_args = []
        for arg in real_args:
            try:
                func_args.append(input[arg])
            except KeyError:
                successfully_used_new_method = False
                func_args.append(None)
                pass

        # if there was at least ONE error just use the old method
        if successfully_used_new_method is True:
            output = func(*func_args)
            if output is not None:
                input.reply(output)
            return
        # else:
        #     print("failed to use new method for func", func, "continuing to old code")
    # ### END: new code ### #

    if args:
        if 'db' in args and 'db' not in input:
            input.db = bot.get_db_connection(input.conn)
        if 'input' in args:
            input.input = input
        if 0 in args:
            out = func(input.inp, **input)
        else:
            kw = dict((key, input[key]) for key in args if key in input)
            out = func(input.inp, **kw)
    else:
        out = func(input.inp)
    if out is not None:
        input.reply(out)


def do_sieve(sieve, bot, input, func, type, args):
    try:
        return sieve(bot, input, func, type, args)
    except Exception:
        print('sieve error', end=' ')
        traceback.print_exc()
        return None


class Handler:
    """Runs plugins in their own threads (ensures order)"""

    def __init__(self, func):
        self.func = func
        self.input_queue = queue.Queue()
        _thread.start_new_thread(self.start, ())

    def start(self):
        uses_db = 'db' in self.func._args
        db_conns = {}
        while True:
            input = self.input_queue.get()

            if input == StopIteration:
                break

            if uses_db:
                db = db_conns.get(input.conn)
                if db is None:
                    db = bot.get_db_connection(input.conn)
                    db_conns[input.conn] = db
                input.db = db

            try:
                run(self.func, input)
            except:
                traceback.print_exc()

    def stop(self):
        self.input_queue.put(StopIteration)

    def put(self, value):
        self.input_queue.put(value)


def dispatch(input: Input, kind, func, args, autohelp=False):
    for sieve, in bot.plugs['sieve']:
        input = do_sieve(sieve, bot, input, func, kind, args)
        if input is None:
            return

    if autohelp and args.get('autohelp', True) and not input.inp and func.__doc__ is not None:
        input.notice(input.conn.conf['command_prefix'] + func.__doc__)
        return

    if func._thread:
        bot.threads[func].put(input)
    else:
        _thread.start_new_thread(run, (func, input))


def match_command(command):
    commands = list(bot.commands)

    # do some fuzzy matching
    prefix = [x for x in commands if x.startswith(command)]
    if len(prefix) == 1:
        return prefix[0]
    elif prefix and command not in prefix:
        return prefix

    return command


def main(conn, out):
    inp = Input(conn, *out)
    command_prefix = conn.conf.get('command_prefix', '.')

    # EVENTS
    for func, args in bot.events[inp.command] + bot.events['*']:
        dispatch(Input(conn, *out), "event", func, args)

    if inp.command == 'PRIVMSG':
        # COMMANDS
        if inp.chan == inp.nick:    # private message, no command prefix
            prefix = '^(?:[' + command_prefix + ']?|'
        else:
            prefix = '^(?:[' + command_prefix + ']|'

        command_re = prefix + inp.conn.nick
        command_re += r'[,;:]+\s+)(\w+)(?:$|\s+)(.*)'

        m = re.match(command_re, inp.lastparam)

        if m:
            trigger = m.group(1).lower()
            command = match_command(trigger)

            if isinstance(command, list):    # multiple potential matches
                input = Input(conn, *out)
                if trigger not in ('b', 'p', 'd', 'pa', 'uj'):  # unobot commands exempt from suggestions
                    input.notice("Did you mean %s or %s?" % (', '.join(command[:-1]), command[-1]))
            elif command in bot.commands:
                input = Input(conn, *out)
                input.trigger = trigger
                input.inp_unstripped = m.group(2)
                input.inp = input.inp_unstripped.strip()

                func, args = bot.commands[command]
                dispatch(input, "command", func, args, autohelp=True)

        # REGEXES
        for func, args in bot.plugs['regex']:
            match = args['re'].search(inp.lastparam)
            if match:
                input = Input(conn, *out)
                input.inp = match

                dispatch(input, "regex", func, args)
