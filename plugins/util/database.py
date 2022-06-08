import log
from sqlite3 import OperationalError
import traceback


# these dont mean anything because when a column is accesed it is automatically auto-created
# yes that's sad but idk i didnt make it
channel_columns  = ['chan NOT NULL',
                    'admins',
                    'permissions',
                    'ops',
                    'bans',
                    'disabled',
                    'ignored',
                    'badwords',
                    'flood',
                    'cmdflood',
                    'trimlength',
                    'autoop',
                    'votekick',
                    'voteban',
                    'primary key(chan)']
user_columns     = ['nick NOT NULL',
                    'mask',
                    'version',
                    'location',
                    'lastfm',
                    'fines',
                    'battlestation',
                    'desktop',
                    'horoscope',
                    'greeting',
                    'waifu',
                    'husbando',
                    'birthday',
                    'homescreen',
                    'snapchat',
                    'mal',
                    'selfie',
                    'fit',
                    'handwriting',
                    'steam',
                    'primary key(nick)']
location_columns = ['location NOT NULL',
                    'latlong',
                    'address',
                    'primary key(location)']

bank_columns = """nick TEXT NOT NULL,
                  money REAL DEFAULT 0,
                  peach INTEGER DEFAULT 0,
                  rose INTEGER DEFAULT 0,
                  cum INTEGER DEFAULT 0,
                  PRIMARY KEY(nick)"""

db_ready = False


def init(db):
    """Init the databases."""
    global db_ready
    if not db_ready:
        db.execute('create table if not exists channels({});'.
                   format(', '.join(channel_columns)))
        db.execute('create table if not exists users({});'.
                   format(', '.join(user_columns)))
        db.execute('create table if not exists location({});'.
                   format(', '.join(location_columns)))
        db.execute('create table if not exists bank({});'.format(bank_columns))
        db.commit()
        db_ready = True


def update(db):
    """Update the database columns."""
    for i in channel_columns[1:-1]:
        try:
            db.execute('alter table channels add column {}'.format(i))
        except OperationalError:
            pass
    for i in user_columns[1:-1]:
        try:
            db.execute('alter table users add column {}'.format(i))
        except OperationalError:
            pass
    for i in location_columns[1:-1]:
        try:
            db.execute('alter table location add column {}'.format(i))
        except OperationalError:
            pass

def field_exists(db,table,matchfield,matchvalue):
    init(db)
    exists = db.execute("SELECT EXISTS(SELECT 1 FROM {} WHERE {}='{}' LIMIT 1);".format(table,matchfield,matchvalue)).fetchone()[0]
    if exists:
        return True
    else:
        return False

def get(db,table,field,matchfield,matchvalue):
    init(db)
    try:
        matchvalue = matchvalue.lower()
    except Exception as e:
        print("[DB ERROR] start:", e)
        traceback.print_exc()
        print("[DB ERROR] end:", e)
        pass
    try:
        result = db.execute("SELECT {} FROM {} WHERE {}='{}';".format(field,table,matchfield,matchvalue)).fetchone()
        if result:
            return result[0]
        else:
            return False
    except Exception as e:
        print("[DB ERROR] start:", e)
        traceback.print_exc()
        print("[DB ERROR] end:", e)
        log.log("***ERROR: SELECT {} FROM {} WHERE {}='{}';".format(field,table,matchfield,matchvalue))


def set(db, table, field, value, matchfield, matchvalue):
    init(db)
    if value is None:
        value = ''
    try:
        matchvalue = matchvalue.lower()
    except Exception as e:
        print("[DB ERROR] start:", e)
        traceback.print_exc()
        print("[DB ERROR] end:", e)
        pass

    if type(value) is str:
        value = value.replace("'", '').replace('\"', '')

    try:
        db.execute("ALTER TABLE {} ADD COLUMN {};".format(table, field))
    except Exception as e:
        print("[DB ERROR] start:", e)
        traceback.print_exc()
        print("[DB ERROR] end:", e)
        pass

    try:
        if field_exists(db, table, matchfield, matchvalue):
            db.execute("UPDATE {} SET {} = '{}' WHERE {} = '{}';".format(table,field,value,matchfield,matchvalue))
        else:
            db.execute("INSERT INTO {} ({},{}) VALUES ('{}','{}');".format(table,field,matchfield,value,matchvalue))
    except Exception as e:
        print("[DB ERROR] start:", e)
        traceback.print_exc()
        print("[DB ERROR] end:", e)
        db.execute('UPDATE {} SET {} = "{}" WHERE {} = "{}";'.format(table,field,value,matchfield,matchvalue))

    db.commit()
    return
