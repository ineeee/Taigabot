from builtins import map
import re
import socket
import _thread
import time
from ssl import CERT_NONE, CERT_REQUIRED, SSLError, wrap_socket

from core.logging import LoggingQueue


def censor(text: str) -> bytes:
    if 'censored_strings' in bot.config:
        words = list(map(re.escape, bot.config['censored_strings']))
        words = '|'.join(words)
        regex = re.compile(f'({words})')
        text = regex.sub('[censored]', text)

    return text


def hack_cast_str_to_bytes(text: str) -> bytes:
    return text.encode('utf-8', 'replace')


def hack_cast_bytes_to_str(data: bytes) -> str:
    return data.decode('utf-8', 'replace')


class crlf_tcp:
    """Handles tcp connections that consist of utf-8 lines ending with crlf"""

    def __init__(self, host: str, port: int, timeout: int = 300):
        self.ibuffer = b''
        self.obuffer = b''
        self.oqueue = LoggingQueue('output')  # lines to be sent out
        self.iqueue = LoggingQueue('input')  # lines that were received
        self.socket = self.create_socket()
        self.host = host
        self.port = port
        self.timeout = timeout

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.TCP_NODELAY)

    def run(self):
        try:
            self.socket.connect((self.host, self.port))
        except Exception:  # TimeoutException | InterruptedError
            print('Timed out')
            time.sleep(5)
            self.run()

        _thread.start_new_thread(self.recv_loop, ())
        _thread.start_new_thread(self.send_loop, ())

    def recv_from_socket(self, nbytes: int = 4096):
        return self.socket.recv(nbytes)

    def get_timeout_exception_type(self):
        return socket.timeout

    def handle_receive_exception(self, error, last_timestamp):
        if time.time() - last_timestamp > self.timeout:
            self.iqueue.put(StopIteration)
            self.socket.close()
            return True
        return False

    def recv_loop(self):
        last_timestamp = time.time()
        while True:
            try:
                data = self.recv_from_socket(4096)
                self.ibuffer += data
                if data:
                    last_timestamp = time.time()
                else:
                    if time.time() - last_timestamp > self.timeout:
                        self.iqueue.put(StopIteration)
                        self.socket.close()
                        return
                    time.sleep(1)
            except (self.get_timeout_exception_type(), socket.error) as e:
                if self.handle_receive_exception(e, last_timestamp):
                    return
                continue

            while b'\r\n' in self.ibuffer:
                line, self.ibuffer = self.ibuffer.split(b'\r\n', 1)
                self.iqueue.put(hack_cast_bytes_to_str(line))  # cast bytes[] to str

    # send_loop runs permanently in its own thread
    # it shits out `self.oqueue` into `self.socket`
    def send_loop(self):
        while True:
            line = self.oqueue.get().splitlines()[0][:500]  # wut?
            self.obuffer += hack_cast_str_to_bytes(line) + b'\r\n'  # cast str to bytes[]
            while self.obuffer:
                sent = self.socket.send(self.obuffer)
                self.obuffer = self.obuffer[sent:]


class crlf_ssl_tcp(crlf_tcp):
    """Handles ssl tcp connetions that consist of utf-8 lines ending with crlf"""

    def __init__(self, host: str, port: int, ignore_cert_errors: bool, timeout: int = 300):
        self.ignore_cert_errors = ignore_cert_errors
        crlf_tcp.__init__(self, host, port, timeout)

    def create_socket(self):
        return wrap_socket(
            crlf_tcp.create_socket(self),
            server_side=False,
            cert_reqs=CERT_NONE if self.ignore_cert_errors else CERT_REQUIRED)

    def recv_from_socket(self, nbytes: int = 4096):
        return self.socket.read(nbytes)

    def get_timeout_exception_type(self):
        return SSLError

    def handle_receive_exception(self, error, last_timestamp):
        # this is terrible
        if 'timed out' not in error.args[0]:
            raise
        return crlf_tcp.handle_receive_exception(self, error, last_timestamp)


irc_prefix_rem = re.compile(r'(.*?) (.*?) (.*)').match
irc_noprefix_rem = re.compile(r'()(.*?) (.*)').match
irc_netmask_rem = re.compile(r':?([^!@]*)!?([^@]*)@?(.*)').match
irc_param_ref = re.compile(r'(?:^|(?<= ))(:.*|[^ ]+)').findall


class IRC:
    """handles the IRC protocol"""
    def __init__(self, name: str, server: str, nick: str, port: int = 6667, channels: list = [], conf: dict = {}):
        self.name = name
        self.channels = channels
        self.conf = conf
        self.server = server
        self.port = port
        self.nick = nick

        self.out = queue.Queue()    # responses from the server are placed here
        # format: [rawline, prefix, command, params, nick, user, host, paramlist, msg]
        self.connect()

        _thread.start_new_thread(self.parse_loop, ())

    def create_connection(self):
        return crlf_tcp(self.server, self.port)

    def connect(self):
        self.conn = self.create_connection()
        _thread.start_new_thread(self.conn.run, ())
        self.set_pass(self.conf.get('server_password'))
        self.set_nick(self.nick)
        self.cmd('USER', [
            conf.get('user', 'uguubot'),
            '0',
            '*',
            conf.get('realname', 'Taigabot')
        ])

    def parse_loop(self):
        while True:
            # get a message from the input queue
            msg = self.conn.iqueue.get()

            if msg == StopIteration:
                self.connect()
                continue

            # parse the message
            if msg.startswith(':'):    # has a prefix
                prefix, command, params = irc_prefix_rem(msg).groups()
            else:
                prefix, command, params = irc_noprefix_rem(msg).groups()
            nick, user, host = irc_netmask_rem(prefix).groups()
            mask = nick + '!' + user + '@' + host
            paramlist = irc_param_ref(params)
            lastparam = ''
            if paramlist:
                if paramlist[-1].startswith(':'):
                    paramlist[-1] = paramlist[-1][1:]
                lastparam = paramlist[-1]
            # put the parsed message in the response queue
            self.out.put([
                msg, prefix, command, params, nick, user, host, mask, paramlist, lastparam
            ])
            # if the server pings us, pong them back
            if command == 'PING':
                self.cmd('PONG', paramlist)

    def set_pass(self, password: str):
        if password:
            self.cmd('PASS', [password])

    def set_nick(self, nick: str):
        self.cmd('NICK', [nick])

    def join(self, channel: str, key: str = None):
        """ makes the bot join a channel """
        if key:
            out = f'JOIN {channel} {key}'
            self.send(out)
        else:
            self.send(f'JOIN {channel}')

        if channel not in self.channels:
            if ',' not in channel:
                self.channels.append(channel)

    def part(self, channel: str):
        """ makes the bot leave a channel """
        self.cmd('PART', [channel])
        if channel in self.channels:
            self.channels.remove(channel)

    def msg(self, target: str, text: str):
        """ makes the bot send a message to a user """
        self.cmd('PRIVMSG', [target, text])

    def ctcp(self, target: str, ctcp_type: str, text: str):
        """ makes the bot send a PRIVMSG CTCP to a target """
        self.cmd('PRIVMSG', [target, f'\x01{ctcp_type} {text}\x01'])

    def cmd(self, command: str, params=None):   # params: ?list
        if params:
            if isinstance(params[-1], bytes):
                params[-1] = hack_cast_bytes_to_str(params[-1])

            # try to accept arguments as str
            params[-1] = ':' + params[-1]
            self.send(command + ' ' + ' '.join(map(censor, params)))
        else:
            self.send(command)

    def send(self, text: str):
        self.conn.oqueue.put(text)


class SSLIRC(IRC):
    def __init__(self,
                 name: str,
                 server: str,
                 nick: str,
                 port: int = 6697,
                 channels: list = [],
                 conf: dict = {},
                 ignore_certs: bool = True):
        self.ignore_cert_errors = ignore_certs
        IRC.__init__(self, name, server, nick, port, channels, conf)

    def create_connection(self):
        return crlf_ssl_tcp(self.server, self.port, self.ignore_cert_errors)
