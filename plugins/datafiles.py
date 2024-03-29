# -*- coding: utf-8 -*-

from util import hook, textgen, text
import random
from random import randint
import json

color_codes = {
    '<r>': '\x02\x0305',
    '<g>': '\x02\x0303',
    '<y>': '\x02'
}

with open('plugins/data/smileys.txt') as f:
    smileys = [line.strip() for line in f.readlines() if not line.startswith('//')]

with open('plugins/data/potato.txt') as f:
    potatoes = [line.strip() for line in f.readlines() if not line.startswith('//')]

with open('plugins/data/8ball_responses.txt') as f:
    responses = [line.strip() for line in f.readlines() if not line.startswith('//')]


with open('plugins/data/larts.txt') as f:
    larts = [line.strip() for line in f.readlines() if not line.startswith('//')]


with open('plugins/data/insults.txt') as f:
    insults = [line.strip() for line in f.readlines() if not line.startswith('//')]


with open('plugins/data/flirts.txt') as f:
    flirts = [line.strip() for line in f.readlines() if not line.startswith('//')]


with open('plugins/data/yiffs.txt') as f:
    yiffs = [line.strip() for line in f.readlines() if not line.startswith('//')]


with open('plugins/data/lewd.txt') as f:
    lewds = [line.strip() for line in f.readlines() if not line.startswith('//')]

with open('plugins/data/slogans.txt') as f:
    slogans = [line.strip() for line in f.readlines() if not line.startswith('//')]

with open('plugins/data/youtube.txt') as f:
    youtube = [line.strip() for line in f.readlines() if not line.startswith('//')]


def get_generator(_json, variables):
    data = json.loads(_json)
    return textgen.TextGenerator(data['templates'], data['parts'], variables=variables)


def send_phrase(inp, attack, nick, conn, me, notice, chan):
    target = inp.strip()
    # if ' ' in target:
    #     notice('Invalid username!')
    #     return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == 'itself':
        target = nick

    values = {
        'user': target,
        'nick': conn.nick,
        'channel': chan,
        'yiffer': nick
    }
    phrase = random.choice(attack)
    # act out the message
    me(phrase.format(**values))
    return


@hook.command(autohelp=False)
def smiley(inp):
    """smiley -- show a random smiley emoticon"""
    return random.choice(smileys)


@hook.command
def potato(inp, me):
    """potato <user> -- Makes <user> a tasty little potato."""

    method = random.choice(['bakes', 'fries', 'boils', 'roasts'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    size = random.choice(['small', 'little', 'mid-sized', 'medium-sized', 'large', 'gigantic'])
    potato_type = random.choice(potatoes)
    inp = inp.strip()
    side_dish = random.choice(['side salad', 'dollop of sour cream', 'piece of chicken', 'bowl of shredded bacon'])

    me(f'{method} a {flavor} {size} {potato_type} potato for {inp} and serves it with a small {side_dish}!')


@hook.command('8ball')
def eightball(input, me):
    """8ball <question> -- The all knowing magic eight ball, in electronic form. Ask and it shall be answered!"""
    magic = text.multiword_replace(random.choice(responses), color_codes)
    me(f'shakes the magic 8 ball... {magic}')
    return


@hook.command
def lart(inp, me, nick, conn, notice, chan):
    """lart <user> -- LARTs <user>."""
    send_phrase(inp, larts, nick, conn, me, notice, chan)
    return


@hook.command
def insult(inp, me, nick, conn, notice, chan):
    """insult <user> -- Makes the bot insult <user>."""
    send_phrase(inp, insults, nick, conn, me, notice, chan)
    return


@hook.command
def flirt(inp, me, nick, conn, notice, chan):
    """flirt <user> -- Makes the bot flirt <user>."""
    send_phrase(inp, flirts, nick, conn, me, notice, chan)
    return


@hook.command(autohelp=False)
def yiff(inp, me, nick, conn, notice, chan):
    """yiff <user> -- yiffs <user>."""
    send_phrase(inp, yiffs, nick, conn, me, notice, chan)
    return


@hook.command(autohelp=False)
def lewd(inp, me, nick, conn, notice, chan):
    """lewd <user> -- lewd <user>."""
    if len(inp) == 0:
        return 'ヽ(◔ ◡ ◔)ノ.･ﾟ*｡･+☆LEWD☆'
    else:
        send_phrase(inp, lewds, nick, conn, me, notice, chan)
    return


@hook.command
def kill(inp, me, nick, conn, notice):
    """kill <user> -- Makes the bot kill <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot kill itself, kill them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    variables = {
        "user": target
    }

    with open("plugins/data/kills.json") as f:
        generator = get_generator(f.read(), variables)

    # act out the message
    me(generator.generate_string())
    return


@hook.command
def slap(inp, me, nick, conn, notice):
    """slap <user> -- Makes the bot slap <user>."""
    target = inp.strip()

    if " " in target:
        notice("Invalid username!")
        return

    # if the user is trying to make the bot slap itself, slap them
    if target.lower() == conn.nick.lower() or target.lower() == "itself":
        target = nick

    variables = {
        "user": target
    }

    with open("plugins/data/slaps.json") as f:
        generator = get_generator(f.read(), variables)

    # act out the message
    me(generator.generate_string())
    return


@hook.command
def slogan(inp):
    """slogan <word> -- Makes a slogan for <word>."""
    out = random.choice(slogans)
    if inp.lower() and out.startswith("<text>"):
        inp = text.capitalize_first(inp)

    return out.replace('<text>', inp)


def get_filename(action, notice):
    # if 'loli' in action: action = 'lolis'
    if 'insult' in action: action = 'insults'
    elif 'kek' in action: action = 'keks'
    elif 'flirt' in action: action = 'flirts'
    elif 'moist' in action: action = 'moists'
    elif 'lewd' in action: action = 'lewds'
    elif 'qt' in action: action = 'qts'
    elif 'urmom' in action: action = 'urmom'
    elif 'honry' in action: action = 'old'
    elif 'old' in action: action = 'old'
    elif 'fortune' in action: action = 'fortunes'
    elif 'slogan' in action: action = 'slogans'
    elif 'troll' in action: action = 'troll'
    elif 'gain' in action: action = 'gainz'
    elif 'nsfw' in action: action = 'nsfw'
    else:
        notice('Invalid action')
        return None
    return action


@hook.command(channeladminonly=True)
def add(inp, notice):
    """add <type> <data> -- appends <data> to <type>.txt"""
    #inp = inp.split('add')[1]
    action = inp.split(' ')[0]
    text = inp.replace(action, '').strip()
    action = get_filename(action, notice)

    if action is None:
        notice('Denied')
        return

    with open(f'plugins/data/{action}.txt', 'a') as file:  # i dont like this
        file.write(f'{text}\n')

    notice('{} added.'.format(action))
    file.close()
    return


def process_text(inp, name, notice):
    # if not inp or inp is int:
    if 'add' in inp:
        add(inp, name, notice)
    else:
        with open(f'plugins/data/{name}.txt') as file:
            lines = [line.strip() for line in file.readlines() if not line.startswith("//")]
        linecount = len(lines) - 1

        if inp and inp.isdigit():
            num = int(inp) - 1
        else:
            num = randint(0, linecount)

        if num > linecount or num < 0:
            return "Theres nothing there baka"

        reply = '\x02[{}/{}]\x02 {}'.format(num+1, linecount+1, lines[num])

        file.close()
        lines = []
        return reply


@hook.command('wailord', autohelp=False)
@hook.command(autohelp=False)
def troll(inp, say, notice):
    """troll -- Trolls on demand"""
    say(process_text(inp, "trolls", notice))
    return


@hook.command(autohelp=False)
def fortune(inp, say, notice):
    """fortune -- Fortune cookies on demand."""
    say(process_text(inp, "fortunes", notice))
    return


@hook.command("kek", autohelp=False)
@hook.command(autohelp=False)
def topkek(inp, say, notice):
    """topkek -- keks on demand."""
    say(process_text(inp, "keks", notice))
    return


@hook.command(autohelp=False)
def lolifile(inp, say, notice):  # TODO remove this
    """loli -- Returns a loli."""
    say("\x02\x034NSFW\x03\x02 {}".format(process_text(inp, "lolis", notice)))
    return


@hook.command(autohelp=False)
def moistcake(inp, say, notice):
    "moistcake -- Moists on demand."
    say(process_text(inp, "moists", notice))
    return


@hook.command(autohelp=False)
def qt(inp, say, notice):
    """qt --  return qts."""
    say(process_text(inp, "qts", notice))
    return


@hook.command(autohelp=False)
def urmom(inp, say, notice):
    """urmom --  return urmom."""
    say(process_text(inp, "urmom", notice))
    return


@hook.command("old", autohelp=False)
@hook.command(autohelp=False)
def honry(inp, say, notice):
    """honry --  return honry."""
    say(process_text(inp, "old", notice))
    return


@hook.command(autohelp=False)
def bender(inp, say):
    """bender -- Bender quotes."""
    benders = ["Bite my shiny, metal ass!", "Bite my glorious, golden ass!", "Bite my shiny, colossal ass!", "Bite my splintery, wooden ass!", "Lick my frozen, metal ass!", "Like most of life's problems, this one can be solved with bending.", "Cheese it!", "Well, I'm boned.", "Hey, sexy mama...wanna kill all humans?", "Oh! Your! God!", "He's pending for a bending!", "This is the worst kind of discrimination - the kind against me!", "In case of emergency, my ass can be used as a flotation device.", "In order to get busy at maximum efficiency, I need a girl with a big, 400-ton booty.", "I'm sick of shaking my booty for these fat jerks!", "Bite my red-hot glowing ass!", "All I know is, this gold says it was the best mission ever.", "Hey, guess what you're all accessories to.", "Well, I don't have anything else planned for today. Let's get drunk!", "Oh, no room for Bender, huh? Fine! I'll go build my own lunar lander! With blackjack and hookers! In fact, forget the lunar lander and the blackjack! Ah, screw the whole thing.", "I found it in the street! Like all the food I cook.", "I can't stand idly by while poor people get free food!", "Congratulations Fry, you've snagged the perfect girlfriend. Amy's rich, she's probably got other characteristics...", "You may need to metaphorically make a deal with the devil. By 'devil' I mean robot devil and by 'metaphorically' I mean get your coat.", "Boy, who knew a cooler could also make a handy wang coffin?", "Call me old fashioned but I like a dump to be as memorable as it is devastating.", "My life, and by extension everyone else's is meaningless.", "Do I preach to you while you're lying stoned in the gutter? No.", "Everybody's a jerk. You, me, this jerk.", "I hate the people that love me and they hate me.", "I've personalized each of your meals. Amy, you're cute, so I baked you a pony!", "Ahh, computer dating. It's like pimping, but you rarely have to use the phrase, 'upside your head'.", "Court’s kinda fun when it’s not my ass on the line!", "Maybe you can interface with my ass! By biting it!", "Well, I'll go build my own theme park! With blackjack and hookers! In fact, forget the park!", "  Compare your lives to mine and then kill yourself!", "I would give up my 8 other senses, even smision, for a sense of taste!", "Stupid anti-pimping laws!", "Blackmail’s such an ugly word. I prefer extortion. The x makes it sound cool.", "Great is ok, but amazing would be great!", "The pie is ready. You guys like swarms of things, right?", "Fry cracked corn, and I don't care; Leela cracked corn, I still don't care; Bender cracked corn, and he is great! Take that you stupid corn!", "Stay away from our women. You got metal fever, baby, metal fever!", "If it ain't black and white, peck, scratch and bite.", "Life is hilariously cruel.", "Pardon me, brother. Care to donate to the anti-mugging you fund?", "I love this planet. I've got wealth, fame, and access to the depths of sleaze that those things bring.", "C'mon, it's just like making love. Y'know, left, down, rotate sixty-two degrees, engage rotors...", "Oh my God, I'm so excited I wish I could wet my pants.", "Argh. The laws of science be a harsh mistress.", "In the event of an emergency, my ass can be used as a floatation device.", "Hey, I got a busted ass here! I don't see anyone kissing it.", "I'm a fraud - a poor, lazy, sexy fraud.", "This'll show those filthy bastards who's loveable!"]
    say(random.choice(benders))
    benders = []
    return


@hook.command('gains', autohelp=False)
@hook.command(autohelp=False)
def gainz(inp, say, notice):
    """gains -- SICK GAINZ BRO"""
    say(process_text(inp, "gainz", notice))
    return


# @hook.command(autohelp=False)
# def nsfw(inp, say, notice):
#     """nsfw -- Have a nice fap"""
#     say(process_text(inp, "nsfw", notice))
#     return
