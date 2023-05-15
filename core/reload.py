import collections
import glob
import os
import re
import sys
import traceback


# FUCK this entire file.
# what the fuck even

if 'mtimes' not in globals():
    mtimes = {}

if 'lastfiles' not in globals():
    lastfiles = set()


def make_signature(f):
    filename = f.__code__.co_filename

    # trim folder path so it doesnt look so verbose
    if filename.startswith('plugins/'):
        filename = filename.replace('plugins/', '')

    return filename, f.__name__, f.__code__.co_firstlineno


def format_plug(plug, kind='', lpad=0):
    msg_filename, msg_function, msg_lineno = make_signature(plug[0])

    out = ' ' * lpad + f'{msg_filename}:{msg_function}:{msg_lineno}'
    if kind == 'command':
        out += ' ' * (50 - len(out)) + plug[1]['name']

    if kind == 'event':
        out += ' ' * (50 - len(out)) + ', '.join(plug[1]['events'])

    if kind == 'regex':
        out += ' ' * (50 - len(out)) + plug[1]['regex']

    return out


def include(filename, namespace):
    file = open(filename, 'r').read()
    code = compile(file, filename, 'exec')
    eval(code, namespace)


def reload(init: bool = False):
    changed = False

    if init:
        bot.plugs = collections.defaultdict(list)
        bot.threads = {}

    core_fileset = set(glob.glob(os.path.join("core", "*.py")))

    for filename in core_fileset:
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            print(f'Loading {filename}')
            mtimes[filename] = mtime

            changed = True

            try:
                include(filename, globals())
            except Exception:
                traceback.print_exc()
                if init:        # stop if there's an error (syntax?) in a core
                    sys.exit(1)  # script on startup
                continue

            if filename == os.path.join('core', 'reload.py'):
                reload(init=init)
                return

    fileset = set(glob.glob(os.path.join('plugins', '*.py')))

    # remove deleted/moved plugins
    for name, data in list(bot.plugs.items()):
        bot.plugs[name] = [x for x in data if x[0]._filename in fileset]

    for filename in list(mtimes):
        if filename not in fileset and filename not in core_fileset:
            mtimes.pop(filename)

    for func, handler in list(bot.threads.items()):
        if func._filename not in fileset:
            handler.stop()
            del bot.threads[func]

    # compile new plugins
    for filename in fileset:
        output = ''
        mtime = os.stat(filename).st_mtime
        if mtime != mtimes.get(filename):
            mtimes[filename] = mtime

            changed = True

            try:
                code = compile(open(filename, 'r').read(), filename, 'exec')
                namespace = {}
                eval(code, namespace)
            except ModuleNotFoundError as e:
                print(f'Error: cant load {filename}, missing a required package. {e}')
                continue
            except Exception:
                traceback.print_exc()
                continue

            # remove plugins already loaded from this filename
            for name, data in list(bot.plugs.items()):
                bot.plugs[name] = [x for x in data
                                   if x[0]._filename != filename]

            for func, handler in list(bot.threads.items()):
                if func._filename == filename:
                    handler.stop()
                    del bot.threads[func]

            for obj in list(namespace.values()):
                if hasattr(obj, '_hook'):  # check for magic
                    if obj._thread:
                        # this is the line that actually loads and runs plugins
                        bot.threads[obj] = Handler(obj)

                    for type, data in obj._hook:
                        bot.plugs[type] += [data]

                        if not init:
                            print(f'### new plugin (type: {type}) loaded:', format_plug(data))

    if changed:
        bot.commands = {}
        for plug in bot.plugs['command']:
            name = plug[1]['name'].lower()
            if not re.match(r'^\w+$', name):
                print('### ERROR: invalid command name "{}" ({})'.format(name, format_plug(plug)))
                continue
            if name in bot.commands:
                print("### ERROR: command '{}' already registered ({}, {})".format(name,
                                                                                   format_plug(bot.commands[name]),
                                                                                   format_plug(plug)))
                continue
            bot.commands[name] = plug

        bot.events = collections.defaultdict(list)
        for func, args in bot.plugs['event']:
            for event in args['events']:
                bot.events[event].append((func, args))

    if init:
        print('  plugin listing:')

        if bot.commands:
            # hack to make commands with multiple aliases
            # print nicely

            print('    command:')
            commands = collections.defaultdict(list)

            for name, (func, args) in list(bot.commands.items()):
                commands[make_signature(func)].append(name)

            for sig, names in sorted(commands.items()):
                names.sort(key=lambda x: (-len(x), x))  # long names first
                out = ' ' * 6 + '%s:%s:%s' % sig
                out += ' ' * (50 - len(out)) + ', '.join(names)
                print(out)

        for kind, plugs in sorted(bot.plugs.items()):
            if kind == 'command':
                continue
            print('    {}:'.format(kind))
            for plug in plugs:
                try:
                    print(format_plug(plug, kind=kind, lpad=6))
                except UnicodeEncodeError:
                    pass
        print()
