from util import hook

                 # (sql name, prefix, suffix)
MEME_CURRENCIES = [("money", "$", " moneis"),
                   ("peach", "🍑", " peachy peaches"),
                   ("rose", "🌹", " rosey roses"),
                   ("cum", "💦", " daddies cummies")]

# check if $nick has an account in the bank
def bank_exists(db, nick):
    cursor = db.execute("SELECT nick FROM bank WHERE nick = ?", (nick, ))
    db.commit()
    # "Fetches the next row of a query result set, returning a single sequence, or None when no more data is available."
    row = cursor.fetchone()

    if row is None:
        return False
    else:
        return True

# create an account for $nick
# make sure the schema has sane DEFAULTs (util/database.py $bank_columns)
def bank_create(db, nick):
    db.execute("INSERT INTO bank(nick) VALUES (?)", (nick, ))
    db.commit()

def bank_get_data(db, nick, currency):
    sql = "SELECT {} FROM bank WHERE nick = ?".format(currency)
    cursor = db.execute(sql, (nick, ))
    db.commit()
    row = cursor.fetchone()

    if row is None:
        return "$0"
    else:
        return row[0]

# get all currencies from $nick
# TODO find a better function name, portfolio doesnt really apply
def bank_get_bals(db, nick):
    data = []
    for (currency, prefix, suffix) in MEME_CURRENCIES:
        value = bank_get_data(db, nick, currency)
        data.append("{}{}{}".format(prefix, value, suffix))

    return '  -  '.join(data)


# subtract one $item from $nick
def bank_subtract(db, nick, item):
    sql = "UPDATE bank SET {} = {} - 1 WHERE nick = ?".format(item, item)
    db.execute(sql, (nick, ))
    db.commit()

# add one $item from $nick
def bank_add(db, nick, item):
    sql = "UPDATE bank SET {} = {} + 1 WHERE nick = ?".format(item, item)
    db.execute(sql, (nick, ))
    db.commit()


@hook.command(autohelp=False)
def bank(inp, nick=None, db=None):
    if not bank_exists(db, nick):
        bank_create(db, nick)
        return "yea hold on i'm creating a new TaigaBank(tm) Account(r) just for you sir dudesir. use \x02.bank\x02 to check it out ok"

    balances = bank_get_bals(db, nick)
    return "{}, your TaigaBank(tm) account: {}".format(nick, balances)


@hook.command(autohelp=False)
def peach(inp, nick=None, db=None, me=None, notice=None):
    if not inp:
        notice("You have to tell me who you're going to send it to")
        return

    if inp == nick:
        return "ur hungry, {}? cant send peachy peaches from you to you".format(nick)

    if not bank_exists(db, inp):
        return "dude {} literally doesnt have a TaigaBank(tm) Account(r), i can't transfer that".format(inp)

    bank_subtract(db, nick, "peach")
    bank_add(db, inp, "peach")

    me(u'gives \U0001F351 to ' + unicode(inp))
    notice("u sent one (1) \U0001F351 peachy peach to {}".format(inp))


@hook.command(autohelp=False)
def rose(inp, nick=None, db=None, me=None, notice=None):
    if not inp:
        notice("You have to tell me who you're going to send it to")
        return

    if inp == nick:
        return "why are you trying to send roses to yourself, {}? weirdo".format(nick)

    if not bank_exists(db, inp):
        return "dude {} literally doesnt have a TaigaBank(tm) Account(r), i can't transfer that".format(inp)

    bank_subtract(db, nick, "rose")
    bank_add(db, inp, "rose")

    if inp.lower() == 'ru':
        me('u gives \U0001F940 to ' + unicode(inp))
    else:
        me('u gives \U0001F339 to ' + unicode(inp))
    notice("u sent one (1) \U0001F339 rosey rose to {}".format(inp))

@hook.command(autohelp=False)
def daddy(inp, nick=None, db=None, me=None, notice=None):
    if nick.lower() = 'daddy':
        if not inp:
            notice("who would u like to daddy, daddio?")
            return

        if inp == nick:
            return "no daddy thats not allowed"

        if not bank_exists(db, inp):
            return "dude {} literally doesnt have a TaigaBank(tm) Account(r)".format(inp)

        bank_add(db, inp, "cum")

        me('u gifted \U0001F4A6 to ' + unicode(inp))
        
        notice("u gifted one (1) \U0001F4A6 cummie to {}".format(inp))
    else:
        notice("only daddy can daddy, non-daddy")

