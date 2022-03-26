from util import hook, database

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
def bank_get_portfolio(db, nick):
    data = []
    for (currency, prefix, suffix) in MEME_CURRENCIES:
        value = bank_get_data(db, nick, currency)
        data.append("{}{}{}".format(prefix, value, suffix))

    return '  -  '.join(data)


@hook.command(autohelp=False)
def bank(inp, nick=None, db=None):
    if not bank_exists(db, nick):
        bank_create(db, nick)
        return "yea hold on i'm creating a new TaigaBank(tm) account just for you sir dudesir. use \x02.bank\x02 to check it out ok. keep in mind that this command doesnt do anything yet"

    portfolio = bank_get_portfolio(db, nick)
    return "{}, your useless TaigaBank(tm) account: {}".format(nick, portfolio)
