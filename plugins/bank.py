from random import choice
from time import time
from util import hook

# format: (sql col name, prefix, suffix)
MEME_CURRENCIES = [('money', '$', ' moneis'),
                   ('peach', '🍑', ' peachy peaches'),
                   ('rose', '🌹', ' rosey roses'),
                   ('cum', '💦', ' daddies cummies')]
last_bene = {}


# check if $nick has an account in the bank
def bank_exists(db, nick: str) -> bool:
    cursor = db.execute('SELECT nick FROM bank WHERE nick = ?', (nick, ))
    db.commit()
    # 'Fetches the next row of a query result set, returning a single sequence, or None when no more data is available.'
    row = cursor.fetchone()

    if row is None:
        return False
    else:
        return True


# create an account for $nick
# make sure the schema has sane DEFAULTs (util/database.py $bank_columns)
def bank_create(db, nick: str) -> None:
    db.execute('INSERT INTO bank(nick) VALUES (?)', (nick, ))
    db.commit()


def bank_get_data(db, nick: str, currency: str) -> str:
    sql = f'SELECT {currency} FROM bank WHERE nick = ?'
    cursor = db.execute(sql, (nick, ))
    db.commit()
    row = cursor.fetchone()

    if row is None:
        return '0'
    else:
        return row[0]


# get all currencies from $nick
# TODO find a better function name, portfolio doesnt really apply
def bank_get_portfolio(db, nick: str) -> str:
    data = []
    for (currency, prefix, suffix) in MEME_CURRENCIES:
        value = bank_get_data(db, nick, currency)
        data.append(f'{prefix}{value}{suffix}')

    return '  -  '.join(data)


# subtract one $item from $nick
def bank_subtract(db, nick: str, item: str) -> None:
    sql = f'UPDATE bank SET {item} = {item} - 1 WHERE nick = ?'
    db.execute(sql, (nick, ))
    db.commit()


# add one $item from $nick
def bank_add(db, nick: str, item: str) -> None:
    sql = f'UPDATE bank SET {item} = {item} + 1 WHERE nick = ?'
    db.execute(sql, (nick, ))
    db.commit()


@hook.command(autohelp=False)
def bank(inp, nick, db):
    """bank -- check the balance in your TaigaBank(tm) Account(r). also opens a new account if you dont have one"""
    if not bank_exists(db, nick):
        bank_create(db, nick)
        return f'{nick}: a new TaigaBank(tm) Account(r) was opened!!1 check out \x02.bank\x02 and \x02.bene\x02'

    portfolio = bank_get_portfolio(db, nick)
    return f'{nick}, your TaigaBank(tm) Account(r): {portfolio}'


@hook.command()
def peachypeach(inp, nick, db, me, notice):
    """peachypeach <nick>: send one (1) peachy peach to nick"""

    if not bank_exists(db, nick):
        return f'{nick}: you need to open a TaigaBank(tm) Account(r) to do that'

    if inp.lower() == nick.lower():
        return f'ur hungry, {nick}? cant send peachy peaches from you to you'

    if not bank_exists(db, inp):
        return f"dude {inp} literally doesnt have a TaigaBank(tm) Account(r), i can't transfer that"

    bank_subtract(db, nick, 'peach')
    bank_add(db, inp, 'peach')

    me(f'gives \U0001F351 to {inp}')
    notice(f'sent one (1) \U0001F351 peachy peach to {inp}')


@hook.command()
def roseyrose(inp, nick, db, me, notice):
    """roseyrose <nick>: send one (1) rosey rose to nick"""

    if not bank_exists(db, nick):
        return f'{nick}: you need to open a TaigaBank(tm) Account(r) to do that'

    if inp.lower() == nick.lower():
        return f'why are you trying to send roses to yourself, {nick}? weirdo'

    if not bank_exists(db, inp):
        return f"dude {inp} literally doesnt have a TaigaBank(tm) Account(r), i can't transfer that"

    bank_subtract(db, nick, 'rose')
    bank_add(db, inp, 'rose')

    if inp.lower() == 'ru':
        me(f'gives \U0001F940 to {inp}')
    else:
        me(f'gives \U0001F339 to {inp}')
    notice(f'sent one (1) \U0001F339 rosey rose to {inp}')


@hook.command()
def daddiescummies(inp, nick, db, me, notice):
    """daddiescummies <nick>: send one (1) daddies cummies to nick"""

    if not bank_exists(db, nick):
        return f'{nick}: you need to open a TaigaBank(tm) Account(r) to do that'

    if inp.lower() == nick.lower():
        return f'{nick} just came all over themselves. weirdo'

    if not bank_exists(db, inp):
        return f"dude {inp} literally doesnt have a TaigaBank(tm) Account(r), i can't transfer that"

    bank_subtract(db, nick, 'cum')
    bank_add(db, inp, 'cum')

    me(f'gives \U0001F4A6 to {inp}')
    notice(f'sent one (1) \U0001F4A6 daddies cummies to {inp}')


@hook.command()
def bene(inp, nick, db, me, notice):
    """bene -- claim one (1) free thing every few minutes"""
    if not bank_exists(db, nick):
        return f'{nick}: you need to open a TaigaBank(tm) Account(r) to get paid. try \x02.bank\x02'

    global last_bene

    # only allow one claim every $allowed_interval seconds
    if nick in last_bene:
        current_ts = time()
        last_ts = last_bene[nick]
        diff = current_ts - last_ts
        allowed_interval = 10 * 60  # seconds
        remaining = allowed_interval - diff

        if diff < allowed_interval:
            return f'please wait {allowed_interval} seconds to claim something again, {nick} ({remaining:.1f} sec left)'

    name, prefix, suffix = choice(MEME_CURRENCIES)
    bank_add(db, nick, name)
    me(f'gives {nick} {prefix}1{suffix}')
    last_bene[nick] = time()

    return
