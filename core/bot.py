import os
import sys
import time
import json
import sqlite3
import _thread


class Bot:
    def __init__(self):
        self.start_time = time.time()
        self.config = {}
        self.config_mtime = 0
        self.conns = {}
        self.db_conns = {}

        # folder used to store database and logs
        self.persist_dir = os.path.abspath('persist')

    def ensure_files(self):
        if not os.path.exists(self.persist_dir):
            os.mkdir(self.persist_dir)

        if not os.path.exists('config'):
            print('ERROR: no config file found!')
            print("Please rename 'config.default' to 'config' to set up your bot!")
            sys.exit(1)

    def load_config(self):
        # reload config from file if file has changed
        config_mtime = os.stat('config').st_mtime
        if self.config_mtime != config_mtime:
            try:
                self.config = json.load(open('config'))
                self.config_mtime = config_mtime
            except ValueError as e:
                print('error: malformed config', e)

    def get_db_connection(self, conn):
        """returns an sqlite3 connection to a persistent database"""
        # at some point i added a print() here and discovered that
        # this gets called 10 times per every irc line. why? TODO fix

        name = '{}.db'.format(conn.name)
        threadid = _thread.get_ident()
        if name in self.db_conns and threadid in self.db_conns[name]:
            return self.db_conns[name][threadid]

        filename = os.path.join(self.persist_dir, name)

        db = sqlite3.connect(filename, timeout=1)
        if name in self.db_conns:
            self.db_conns[name][threadid] = db
        else:
            self.db_conns[name] = {threadid: db}

        return db

    def get_api_key(self, key):
        if 'api_keys' not in self.config:
            raise Exception('The bot does not have a valid config file')

        return self.config['api_keys'].get(key, None)
