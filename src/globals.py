import discord
import os
import requests
import random
import json
from discord.ext import commands
# from replit import db

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example',
                   intents=intents)
bot.remove_command('help')

# -- GLOBAL VARIABLES -- #

with open("db.json", "r") as read_content:
    db = json.load(read_content)

# tokens
if 'bot_token' in os.environ:
    bot_token = os.environ['bot_token']
else:
    bot_token = os.environ['dbot_token']  # dev bot token
unsplash_token = os.environ['unsplash_key']
rapid_api = os.environ['rapidapi_key']
dictionary_key = os.environ['dictionary_key']
my_user_id = int(os.environ['my_user_id'])
drew_id = 382364782365376512
nyt_key = os.environ['nyt_key']
mw_dict_key = os.environ['mw_dict_key']  # merriam-webster dictionary key
mw_thes_key = os.environ['mw_thes_key']  # merriam-webster thesaurus key
wordnik_key = os.environ['wordnik_key']
# pip install google-cloud-translate==2.0.1

os.environ['MPLCONFIGDIR'] = "config/matplotlib"

# gif links
no_gif = "https://tenor.com/view/no-i-dont-think-i-will-captain-america-old-capt-gif-17162888"
straining_gif = "https://tenor.com/view/straining-gif-6190466"
finger_wag = "https://tenor.com/view/nope-no-shake-finger-shake-finger-gif-4138495"
annoyed = "https://tenor.com/view/kabangu-upset-annoyed-gif-14814728"
nope = "https://tenor.com/view/shannon-sharpe-undisputed-nope-no-smh-gif-12504325"

user_map = {
    "382364782365376512": "Shroombo",
    "547127905679966209": "CerealGuy69",
    "110537131499225088": "Little_G",
    "516416338579947521": "MarcusAntonious99",
    "594275046982287384": "\u300cO B A G\u300d",
    "247833945956155393": "Maree\u2212p Fall",
    "360945793609236490": "Slongdong69",
    "267467160731779072": "Gnardo",
    "887714761666600960": "Obotoma Dev",
    "887681266068111362": "Obotma",
    "417104202930585614": "looksgoodnshorts",
    "439205512425504771": "NotSoBot"
}
message_map = {} # session-based map that tracks who's reacted to what messages (dynamic udefine stats in Text.py)
votes = {}


# --GLOBAL FUNCTIONS--
async def random_fact(message):
    random_decorator = ["trivia", "math", "date", "year"]
    response = requests.get(
        f'http://numbersapi.com/random/' +
        random_decorator[random.randrange(0,
                                          len(random_decorator) - 1)] +
        '?json').json()['text']
    await message.channel.send(response)
    random_adjective = [
        'tidy', 'nifty', 'captivating', 'good', 'great', 'cool', 'elegant',
        'dandy', 'tasteful', 'groovy', 'clean', 'peachy', 'arresting', 'keen',
        'refined', 'adroit', 'straight', 'corking', 'smashing', 'bully',
        'stimulating', 'swell', 'riveting', 'alluring', 'appealing',
        'cracking', 'undiluted', 'bang-up', 'full-strength', 'not bad',
        'slap-up', 'nice', 'lovely', 'clever', 'wonderful', 'fantastic',
        'stirring', 'wondrous', 'stunning', 'classy', 'awesome', 'amazing',
        'amusing', 'interesting', 'beautiful', 'engrossing', 'brilliant',
        'terrific', 'cute', 'simple', 'fun', 'gorgeous', 'groovin', 'snazzy',
        'crisp', 'spiffy', 'crafty', 'fancy', 'ingenious', 'sweet', 'pretty',
        'skilful', 'purty', 'wow', 'handsome', 'fine', 'well', 'chic',
        'flawless', 'shipshape', 'leggy', 'clear', 'impeccable', 'pure',
        'astute', 'spotless', 'precise', 'shrewd', 'careful', 'spruce',
        'distinct', 'goody', 'organzied', 'resourceful', 'unadulterated',
        'orderly', 'super', 'formidable', 'trim', 'curious', 'rigorous',
        'ordered', 'good-looking', 'kiln-dried', 'nice-looking', 'delightful',
        'poggers', 'systematic', 'epic', 'enthralling', 'fabulous',
        'presentable', 'pleasing', 'splendid'
    ]
    await message.channel.send(
        f'Aren\'t numbers so ' +
        random_adjective[random.randrange(0,
                                          len(random_adjective) - 1)] + '?')

async def update_ses(entry, update_message):
    db[entry] = update_message
    await update_db()

async def add_emoji(message, emoji_name, emojis):
    for emoji in emojis:
        if emoji.name == emoji_name:
            await message.add_reaction(emoji)


async def send_gif(term, limit):
    # set the apikey and limit
    apikey = os.environ['gif_key']  # test value

    # get the top <limit> GIFs for the search term
    r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" %
                     (term, apikey, limit))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_gifs = json.loads(r.content)['results']
        rand_url = top_gifs[random.randrange(0, limit - 1)]['url']
        return rand_url
    else:
        return None

# returns role_id as an int. Returns None if not found
async def get_role(ctx, name):
    role_id = None
    for role in ctx.guild.roles:
        if role.name == name:
            role_id = role.id
    return role_id

# gets custom emoji from guild
async def get_emoji(guild, emoji_name):
    for emoji in guild.emojis:
        if emoji.name == emoji_name:
            return emoji
    return None

async def update_db():
  global db
  with open("db.json", "w") as outfile:
    json.dump(db, outfile)
  with open("db.json", "r") as read_content:
    db = json.load(read_content)
