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

def bank_money_update(db, nick, item, newbal):
    sql = "UPDATE bank SET {} = {} WHERE nick = ?".format(item, newbal)
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
    if nick.lower() == 'daddy':
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





# HONK HONK
actions = {
    "honk": ["honked at", "honking"],
    "pet": ["pet", "petting"],
    "diddle": ["diddled", "diddling"],
    "spank": ["spanked", "spanking"],
    "rape": ["raped", "raping"],
    "sex": ["sexed", "sexing"],
    "lick": ["licked", "licking"]
}


def citation(db, chan, nick, reason):
    fine = float(random.randint(1, 1500))
    floatfine = float(str(random.random())[0:4])
    if reason.split()[1] == 'raping':
        fine = float(random.randint(1500, 3000))
    if nick.lower() == 'myon':
        fine = floatfine
    elif nick.lower() == 'wednesday\'s mixtape':
        fine = 1337.69
    else:
        fine = fine + floatfine
    if 'buy' in reason:
        thing = nick
        nick = reason.split(' ')[1]
        try:
            totalfines = float(bank_get_bals(db, nick, money)) + fine
        except:
            totalfines = 0.0 + fine
        bank_money_update(db, nick, money, totalfines)
        strfines = "{:,}".format(totalfines)
        strfine = "{:,}".format(fine)
        if '-' in strfines[0]:
            return u"PRIVMSG {} :\x01ACTION buys {} for \x02${}\x02 {} has \x0309${}\x01".format(
                chan, thing, strfine, nick, strfines[1:])
        if totalfines <= 0:
            return u"PRIVMSG {} :\x01ACTION buys {} for \x02${}\x02 {} owes \x0309${}\x01".format(
                chan, thing, strfine, nick, strfines)
        else:
            return u"PRIVMSG {} :\x01ACTION buys {} for \x02${}\x02. {} owes \x0304${}\x02\x01".format(
                chan, thing, strfine, nick, strfines)
    if 'sell' in reason:
        thing = nick
        nick = reason.split(' ')[1]
        try:
            totalfines = float(bank_get_bals(db, nick, money)) - fine
        except:
            totalfines = 0.0 - fine
        bank_money_update(db, nick, money, totalfines)
        strfines = "{:,}".format(totalfines)
        strfine = "{:,}".format(fine)
        if '-' in strfines[0]:
            return u"PRIVMSG {} :\x01ACTION sells {} for \x02${}\x02 {} has \x0309${}\x01".format(
                chan, thing, strfine, nick, strfines[1:])
        if totalfines <= 0:
            return u"PRIVMSG {} :\x01ACTION sells {} for \x02${}\x02 {} owes \x0309${}\x01".format(
                chan, thing, strfine, nick, strfines)
        else:
            return u"PRIVMSG {} :\x01ACTION sells {} for \x02${}\x02. {} owes \x0304${}\x02\x01".format(
                chan, thing, strfine, nick, strfines)
    if 'shill' in reason:
        thing = nick
        nick = reason.split(' ')[1]
        try:
            totalfines = float(bank_get_bals(db, nick, money)) - fine
        except:
            totalfines = 0.0 - fine
        bank_money_update(db, nick, money, totalfines)
        strfines = "{:,}".format(totalfines)
        strfine = "{:,}".format(fine)
        if '-' in strfines[0]:
            return u"PRIVMSG {} :\x01ACTION shills {} for \x02${}\x02 {} has \x0309${}\x01".format(
                chan, thing, strfine, nick, strfines[1:])
        if totalfines <= 0:
            return u"PRIVMSG {} :\x01ACTION shills {} for \x02${}\x02 {} owes \x0309${}\x01".format(
                chan, thing, strfine, nick, strfines)
        else:
            return u"PRIVMSG {} :\x01ACTION shills {} for \x02${}\x02. {} owes \x0304${}\x02\x01".format(
                chan, thing, strfine, nick, strfines)
    else:
        try:
            totalfines = float(bank_get_bals(db, nick, money)) + fine
        except:
            totalfines = 0.0 + fine
        bank_money_update(db, nick, money, totalfines)
        strfines = "{:,}".format(totalfines)
        strfine = "{:,}".format(fine)
        if '-' in strfines[0]:
            return u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 {}. You have: \x0309${}\x02\x01".format(
                chan, nick, strfine, reason, strfines[1:])
        if totalfines <= 0:
            return u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 {}. You owe: \x0304${}\x02\x01".format(
                chan, nick, strfine, reason, strfines)
        else:
            return u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 {}. You owe: \x0304${}\x02\x01".format(
                chan, nick, strfine, reason, strfines)


@hook.command(autohelp=False)
def bet(inp, nick=None, db=None, chan=None):
    "bet <ammount> -- bets <ammount>"
    inp = inp.replace(',', '').replace('$', '')
    try:
        balance = float(bank_get_bals(db, nick, money))
    except:
        balance = 0.0
    if inp == "":
        inp = "100"
    if inp != "0":
        inp = float('-' + inp)
        if math.isnan(inp):
            return
        strinp = "{:,}".format(inp)
        strmoney = "{:,}".format(balance)
        if inp < balance or balance == 0:
            if '-' in strmoney[0]:
                return u"\x01ACTION You don't have enough money to bet \x02${}\x02. You have \x0309${}\x02\x01".format(
                    strinp[1:], strmoney[1:])
            else:
                return u"\x01ACTION You don't have enough money to bet \x02${}\x02. You owe \x0304${}\x02\x01".format(
                    strinp[1:], strmoney)
            if inp == 0:
                if '-' in strmoney[0]:
                    return u"\x01ACTION You have to bet more than \x02${}\x02. You have \x0309${}\x02\x01".format(
                        strinp[1:], strmoney[1:])
                else:
                    return u"\x01ACTION You have to bet more than \x02${}\x02. You owe \x0304${}\x02\x01".format(
                        strinp[1:], strmoney)
        else:
            print(inp)
            if random.randint(1, 100) <= 50:
                newmoney = balance - inp
                strinp = "{:,}".format(inp)
                strmoney = "{:,}".format(balance)
                bank_money_update(db, nick, money, balance)
                if '-' in strmoney[0]:
                    return u"\x01ACTION You lose the bet and lost \x02${}\x02. You have \x0309${}\x02\x01".format(
                        strinp[1:], strmoney[1:])
                else:
                    return u"\x01ACTION You lose the bet and lost \x02${}\x02. You owe \x0304${}\x02\x01".format(
                        strinp[1:], strmoney)
            else:
                balance = balance + inp
                strinp = "{:,}".format(inp)
                strmoney = "{:,}".format(balance)
                bank_money_update(db, nick, money, balance)
                if '-' in strmoney[0]:
                    return u"\x01ACTION You win the bet and win \x02${}\x02. You have \x0309${}\x02\x01".format(
                        strinp[1:], strmoney[1:])
                else:
                    return u"\x01ACTION You win the bet and win \x02${}\x02. You owe \x0304${}\x02\x01".format(
                        strinp[1:], strmoney)


@hook.command('sell', autohelp=False)
@hook.command('shill', autohelp=False)
@hook.command('sex', autohelp=False)
@hook.command('buy', autohelp=False)
@hook.command('rape', autohelp=False)
@hook.command('spank', autohelp=False)
@hook.command('diddle', autohelp=False)
@hook.command('pet', autohelp=False)
@hook.command('lick', autohelp=False)
@hook.command(autohelp=False)
def honk(inp, nick=None, conn=None, chan=None, db=None, paraml=None, input=None):
    "honk <nick> -- Honks at someone."
    # if pm
    if input.raw.split(' ')[2] == conn.nick:
        chan = input.nick
    else:
        chan = input.raw.split(' ')[2]
    regex = re.compile("(\x1f|\x1d|\x03[1-9]|\x02|\x16)", re.UNICODE)
    paraml[-1] = regex.sub('', paraml[-1])
    target = inp.strip()
    command = paraml[-1].split(' ')[0][1:].lower()
    thing = paraml[-1].split(' ')[1:]
    thing = '|'.join(thing).replace('|', ' ')
    try:
        if thing[-1] == ' ':
            thing = thing[0:-1]
    except IndexError:
        thing = input.nick
    if command == 'sell':
        randnum = random.randint(1, 4)
        if len(inp) == 0:
            if random.randint(1, 3) == 2:
                out = citation(db, chan, thing, 'sell {}'.format(nick))
            else:
                out = u"PRIVMSG {} :\x01ACTION drops {} in a lake.\x01".format(chan, thing)
        else:
            if randnum == 1:
                out = citation(db, chan, thing, 'sell {}'.format(nick))
            elif randnum == 2:
                out = citation(db, chan, thing, 'sell {}'.format(nick))
            elif randnum == 3:
                out = citation(db, chan, thing, 'sell {}'.format(nick))
            else:
                out = u"PRIVMSG {} :\x01ACTION drops {} in a lake.\x01".format(chan, thing)
    elif command == 'shill':
        randnum = random.randint(1, 4)
        if len(inp) == 0:
            if random.randint(1, 3) == 2:
                out = citation(db, chan, thing, 'shill {}'.format(nick))
            else:
                fine = float(random.randint(1500, 3000))
                nick = input.nick
                try:
                    totalfines = float(bank_get_bals(db, nick, money)) + fine
                except:
                    totalfines = 0.0 + fine
                bank_money_update(db, nick, money, totalfines)
                fine = "{:,}".format(fine)
                totalfines = "{:,}".format(totalfines)
                out = u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 for breaking the NDA. You have: \x0309${}\x02\x01".format(
                    chan, nick, fine, totalfines[1:])
        else:
            if randnum == 1:
                out = citation(db, chan, thing, 'shill {}'.format(nick))
            elif randnum == 2:
                out = citation(db, chan, thing, 'shill {}'.format(nick))
            elif randnum == 3:
                out = citation(db, chan, thing, 'shill {}'.format(nick))
            else:
                fine = float(random.randint(1500, 3000))
                nick = input.nick
                try:
                    totalfines = float(bank_get_bals(db, nick, money)) + fine
                except:
                    totalfines = 0.0 + fine
                bank_money_update(db, nick, money, totalfines)
                fine = "{:,}".format(fine)
                totalfines = "{:,}".format(totalfines)
                if totalfines[0] == "-":
                    out = u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 for breaking the NDA. You have: \x0309${}\x02\x01".format(
                        chan, nick, fine, totalfines[1:])
                else:
                    out = u"PRIVMSG {} :\x01ACTION fines {} \x02${}\x02 for breaking the NDA. You owe: \x0304${}\x02\x01".format(
                        chan, nick, fine, totalfines)
    elif command == 'buy':
        randnum = random.randint(1, 4)
        if len(inp) == 0:
            if random.randint(1, 3) == 2:
                out = citation(db, chan, thing, 'buy {}'.format(nick))
            else:
                out = u"PRIVMSG {} :\x01ACTION pisses on the floor and leaves.\x01".format(chan)
        else:
            if randnum == 1:
                out = citation(db, chan, thing, 'buy {}'.format(nick))
            elif randnum == 2:
                out = citation(db, chan, thing, 'buy {}'.format(nick))
            elif randnum == 3:
                out = citation(db, chan, thing, 'buy {}'.format(nick))
            else:
                out = u"PRIVMSG {} :\x01ACTION pisses on the floor and leaves.\x01".format(chan)
    else:
        if len(inp) == 0:
            if random.randint(1, 3) == 2:
                out = citation(db, chan, nick, "for {}".format(actions[command][1]))
            else:
                out = u"PRIVMSG {} :\x01ACTION {}s {}\x01".format(chan, command, nick)
        else:
            randnum = random.randint(1, 4)
            if randnum == 1:
                out = citation(db, chan, nick, "for {}".format(actions[command][1]))
            elif randnum == 2:
                out = citation(db, chan, target,
                               "for being too lewd and getting {}".format(actions[command][0]))
            else:
                out = u"PRIVMSG {} :\x01ACTION {}s {}\x01".format(chan, command, target)
    conn.send(out)


@hook.command('give')
@hook.command
def donate(inp, db=None, nick=None, chan=None, conn=None, notice=None):
    """donate <user> <money> -- Gives <money> to <user>."""
    inp = inp.replace('$', '').replace('-', '').split(' ')
    inp = ' '.join(inp[0:2]).split('.')[0].split()
    user = str(' '.join(inp[0:-1]).split('.')[0])
    donation = float(inp[-1])
    if math.isnan(donation) or math.isinf(donation):
        return
    # try:
    #     donation = inp[-1].split('.')[0] + '.' + inp[-1].split('.')[1][0:2]
    #     print donation
    #     donation = float(donation)
    # except Exception as e:
    #     print e
    #     return
    #if donation > 10000.00:
    #    donation = 10000.00
    if user.lower() == nick.lower():
        user = 'wednesday'
    try:
        giver = float(bank_get_bals(db, nick, money))
    except:
        giver = 0.0
    try:
        taker = float(bank_get_bals(db, user, money))
    except:
        taker = 0.0
    if donation > giver or donation < 0:
        return
    if str(giver)[0] == '-':
        giver = giver + donation
    else:
        giver = giver - donation
    # database.set(db, 'users', 'fines', giver, 'nick', nick)
    # wednesdaywins = random.randint(1, 80)
    # if wednesdaywins == 80:
    #     wednesday = float(database.get(db, 'users', 'fines', 'nick', 'wednesday'))
    #     database.set(db, 'users', 'fines', wednesday - donation, 'nick', 'wednesday')
    #     conn.send(u"PRIVMSG {} :\x01ACTION gives \x02${}\x02 to wednesday.\x01".format(
    #         chan, donation))
    if giver != taker:
        bank_money_update(db, nick, money, giver)
        bank_money_update(db, user, money, taker + donation)
    conn.send(u"PRIVMSG {} :\x01ACTION gives \x02${}\x02 to {}.\x01".format(
        chan, donation, user))


@hook.command('steal')
@hook.command('rob')
@hook.command()
def mug(inp, db=None, nick=None, chan=None, conn=None, notice=None):
    """mug <user> -- Takes money from <user>.."""
    inp = inp.split()
    user = inp[0]
    spoils = float(random.randint(20, 1500))
    try:
        spoils = inp[-1].split('.')[0] + '.' + inp[-1].split('.')[1][0:2]
        spoils = float(spoils)
    except:
        pass
    try:
        robber = float(bank_get_bals(db, nick, money))
    except:
        robber = 0.0
    try:
        victim = float(bank_get_bals(db, user, money))
    except:
        victim = 0.0
    robbingfails = random.randint(1, 3)
    if robbingfails == 2:
        if victim != robber:
            bank_money_update(db, nick, money, robber - spoils)
            bank_money_update(db, user, money, victim + spoils)
            database.set(db, 'users', 'fines', victim - money, 'nick', user)
        conn.send(u"PRIVMSG {} :\x01ACTION {} shoots you in the foot and takes \x02${}\x02.\x01".
                  format(chan, user, spoils))
    else:
        if robber != victim:
            bank_money_update(db, nick, money, robber + spoils)
            bank_money_update(db, user, money, victim - spoils)
        conn.send(u"PRIVMSG {} :\x01ACTION {} shanks {} in a dark alley and takes \x02${}\x02\x01".
                  format(chan, nick, user, spoils))


@hook.command(autohelp=False)
def owed(inp, nick=None, conn=None, chan=None, db=None):
    """owe -- shows your total fines"""
    if '@' in inp: nick = inp.split('@')[1].strip()
    fines = bank_get_bals(db, nick, money)
    if not fines: fines = 0
    strfines = "{:,}".format(float(fines))
    if '-' in strfines[0]:
        return u'\x02{} has:\x02 \x0309${}'.format(nick, strfines[1:])
    if fines <= 0:
        return u'\x02{} owes:\x02 \x0309${}'.format(nick, strfines)
    else:
        return u'\x02{} owes:\x02 \x0304${}'.format(nick, strfines)


# @hook.command(autohelp=False)
# def pay(inp, nick=None, conn=None, chan=None, db=None):
#     """pay -- pay your fines"""
#     return u'\x02Donate to infinitys paypal to pay the fees! \x02'