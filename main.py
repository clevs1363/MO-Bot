import asyncio
import discord
import os
import requests
import random
import youtube_dl
import json
import math
import schedule
import time
import threading
from datetime import date, datetime, timedelta
from discord.ext import commands, tasks
from keep_alive import keep_alive
from replit import db

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# -- GLOBAL VARIABLES -- #

# tokens
# bot_token = os.environ['bot_token']
bot_token = os.environ['dbot_token'] # dev bot token
unsplash_token = os.environ['unsplash_key']
rapid_api = os.environ['rapidapi_key']
dictionary_key = os.environ['dictionary_key']



# gif links
no_gif = "https://tenor.com/view/no-i-dont-think-i-will-captain-america-old-capt-gif-17162888"
straining_gif = "https://tenor.com/view/straining-gif-6190466"
finger_wag = "https://tenor.com/view/nope-no-shake-finger-shake-finger-gif-4138495"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example', intents=intents)
bot.remove_command('help')

class YTDLSource(discord.PCMVolumeTransformer):
  def __init__(self, source, *, data, volume=0.5):
      super().__init__(source, volume)

      self.data = data

      self.title = data.get('title')
      self.url = data.get('url')

  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
      loop = loop or asyncio.get_event_loop()
      data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

      if 'entries' in data:
          # take first item from a playlist
          data = data['entries'][0]

      filename = data['url'] if stream else ytdl.prepare_filename(data)
      return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    bot.loop.create_task(self.audio_player_task())

  songs = asyncio.Queue()
  play_next_song = asyncio.Event()

  async def audio_player_task(self):
    while True:
      self.play_next_song.clear()
      current = await self.songs.get() # dequeue
      current[1].voice_client.play(current[0], after=self.toggle_next)
      await self.play_next_song.wait()

  # called if a song is already playing
  def toggle_next(self, err):
    bot.loop.call_soon_threadsafe(self.play_next_song.set)

  @commands.command()
  async def join(self, ctx):
    try:
      channel = ctx.message.author.voice.channel
    except AttributeError:
      await ctx.send("can't ses unless you're in a voice chat")
      return

    """Joins a voice channel"""

    if ctx.voice_client is not None:
      return await ctx.voice_client.move_to(channel)

    await channel.connect()

  @commands.command(pass_context=True)
  async def play(self, ctx, *, url):
    await ctx.invoke(self.bot.get_command('join'))

    """Streams from a url (same as yt, but doesn't predownload)"""

    async with ctx.typing():
      p = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      await self.songs.put((p, ctx)) # add to queue

      await ctx.send(f'Added to queue: {p.title}')
      if not url.startswith('http'):
        # if the query was not a url, send the url
        await ctx.send(p.data['webpage_url'])

class Text(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    # if 'requests' in db.keys():
    #   del db['requests']

  # 
  # <-- TRIGGERED EVENTS -->
  #

  @bot.event
  async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
      # ignore own messages
      return

    # hkh, ignores links and commands
    if not message.clean_content.startswith('http') and not message.clean_content.startswith('!'):
      if message.content.endswith('er'):
        last = (message.content.split()[-1]).replace("?", "")
        await message.channel.send(last + "? I 'ardly knew 'er!")
      elif message.content.endswith('er?') or message.content.endswith('*r?'):
        await message.channel.send("I \'ardly knew \'er!")
      elif message.content.endswith('*r'):
        await message.channel.send("Censor? I 'ardly knew 'er!")

    # random fact
    if '37' in message.content and not message.content.startswith('http'):
      # ignore emotes of form <:emote:12439824598248>
      if '<' in message.content and '>' in message.content:
        return
      await random_fact(message)

  @bot.event
  async def on_message_edit(before, after):
    # add edit emoji to edited messages
    if not before.content.startswith('http'):
      await add_emoji(after, 'edited')
    return # exit if not found

  @bot.event
  async def on_member_update(before, after):
    activity_type = None
    try:
      activity_type = after.activity.type
    except:
      pass
    if activity_type is discord.ActivityType.streaming:
      # Do X if he is streaming
      channel = bot.get_channel(604834176645988354)
      await channel.send(after.display_name + 'is LIVE! Come in here or he\'ll come for your toes!' + '\n' + after.activity.name + '\n' + after.activity.url)
    else:
      pass

  # 
  # <-- COMMANDS -->
  #
  
  @commands.command()
  async def help(self, ctx):
    await ctx.send(
      """```
--MUSIC--
!play <url>: plays YouTube video from given url. Must be in a voice chat
!play <query>: searches and plays YouTube audio with given query. Must be in a voice chat
!join: have a friend join you in voice chat
--REQUESTS--
!request <text>: add a feature request to a queue, up to 15
!request: use without arguments to show the numbered list of requests
!delete_request <number>: deletes request of given number
--MEMES--
!pun: sends a random pun
!lenny: send 1 or more lennies
--MISCELLANEOUS--
!ses: Gives the time, date, and location of the next ses
!nature <query>: fetches image related to query
!hug: send hugs
!help: Show this message```""")

  @commands.command()
  async def die(self, ctx):
    async with ctx.typing():
      await ctx.send("I'd rather die standing than live kneeling")
      await ctx.send("And I don't even have legs")

  @commands.command()
  async def hug(self, ctx):
    url = await send_gif("hug", 50)
    await ctx.send(url)

  @commands.command()
  async def nature(self, ctx, *, query):
    image = requests.get(f'https://api.unsplash.com/photos/random?query=' + query + '&client_id=' + unsplash_token).json()['urls']['regular']
    await ctx.send(image)
  
  @commands.command()
  async def lenny(self, ctx, num=1):
    if num > 500:
      await ctx.send("Error 37: lenny overflow")
      return
    if num > 100:
      await ctx.send(straining_gif)
    async with ctx.typing():
      lenny = requests.get("https://api.lenny.today/v1/random?limit=%s" % (num)).json()
      if lenny:
        total_lennies = ""
        for l in lenny:
          total_lennies += l['face']
        if len(total_lennies) > 4000:
          # split up into separate messages if necessary
          for x in range(math.floor(len(total_lennies)/2000)):
            await ctx.send(total_lennies[x*2000:(x+1)*2000])
        else:
          await ctx.send(total_lennies)

  @commands.command()
  async def pun(self, ctx):
    # get random
    pun = requests.get("https://dad-jokes.p.rapidapi.com/random/joke?rapidapi-key=%s" % (rapid_api)).json()
    print(pun)
    if pun['success']:
      async with ctx.typing():
        pun = pun['body'][0]
        if pun['NSFW']:
          await ctx.send("Oh, this one's a nasty one.")

        await ctx.send(pun['setup'])

        def check(m):
          return m.channel == ctx.channel

        await bot.wait_for('message', check=check)
        await ctx.send(pun['punchline'])


  @commands.command()
  async def request(self, ctx, *req):
    if 'requests' in db.keys() and len(db['requests']) > 15:
      await ctx.send('Too many features. Delete one or tell my dev to move his ass.')
      return
    if req:
      # add request to dictionary
      if 'requests' in db.keys():
        db['requests'][" ".join(req)] = ctx.message.author.name
      else:
        db['requests'] = {" ".join(req): ctx.message.author.name}
      await add_emoji(ctx.message, "pepehap")
      await ctx.send("\U0001F60E" + "\U0001F44D")
      await ctx.send("You are number %s in the queue" % (len(db['requests'])))
    else:
      # list requests
      ret_string = ""
      counter = 1
      for item in db['requests'].keys():
        ret_string += str(counter) + '. ' + item + '\n'
        counter += 1
      if counter == 1:
        # requests are empty
        await ctx.send("No features requested yet")
      else:
        await ctx.send(ret_string)
  
  @commands.command()
  async def delete_request(self, ctx, num):
    counter = 1
    for request in db['requests'].keys():
      if counter == int(num):
        if ctx.message.author.name == db['requests'][request] or ctx.message.author.name == "CerealGuy69":
          db['requests'].pop(request)
          await ctx.send("yoink")
        else:
          await ctx.send("Not very cash money of you to try and delete someone else's request")
          await ctx.send(finger_wag)
      counter += 1

  @commands.command()
  async def ses(self, ctx, *msg):
    async with ctx.typing():
      await add_emoji(ctx.message, 'ses')
      if msg: # check if arguments were passed
        if ctx.author.name == "CerealGuy69":
          output = " ".join(msg)
          await ctx.message.channel.edit(topic = output)
          await update_ses('ses', output)
          await ctx.send('--SESSION CHANGED--')
        else:
          await ctx.send(no_gif)
          return
      await ctx.send(db['ses'])
  
  @commands.command()
  async def abyses(self, ctx, *msg):
    await add_emoji(ctx.message, 'ses')
    if msg: # check if arguments passed
      if ctx.author.name == "Ś̶̨h̸̥͌r̷̬̍ö̷͉o̴̡͐m̶̧̏b̴̳̆o̵̎͜" or ctx.author.name == "CerealGuy69":
        output = " ".join(msg)
        await ctx.message.channel.edit(topic = output)
        await update_ses('abyses', output)
        await ctx.send('--SESSION CHANGED--')
      else:
        await ctx.send(no_gif)
        return
    await ctx.send(db['abyses'])

  @commands.command()
  async def release(self, ctx):
    if ctx.message.author.name == "CerealGuy69":
      async with ctx.typing():
        await ctx.send("New features added! Check !help for help")

async def random_fact(message):
  random_decorator = ["trivia", "math", "date", "year"]
  response = requests.get(f'http://numbersapi.com/random/' + random_decorator[random.randrange(0, len(random_decorator) - 1)] + '?json').json()['text']
  await message.channel.send(response)
  random_adjective = ['tidy', 'nifty', 'captivating', 'good', 'great', 'cool', 'elegant', 'dandy', 'tasteful', 'groovy', 'clean', 'peachy', 'arresting', 'keen', 'refined', 'adroit', 'straight', 'corking', 'smashing', 'bully', 'stimulating', 'swell', 'riveting', 'alluring', 'appealing', 'cracking', 'undiluted', 'bang-up', 'full-strength', 'not bad', 'slap-up', 'nice', 'lovely', 'clever', 'wonderful', 'fantastic', 'stirring', 'wondrous', 'stunning', 'classy', 'awesome', 'amazing', 'amusing', 'interesting', 'beautiful', 'engrossing', 'brilliant', 'terrific', 'cute', 'simple', 'fun', 'gorgeous', 'groovin', 'snazzy', 'crisp', 'spiffy', 'crafty', 'fancy', 'ingenious', 'sweet', 'pretty', 'skilful', 'purty', 'wow', 'handsome', 'fine', 'well', 'chic', 'flawless', 'shipshape', 'leggy', 'clear', 'impeccable', 'pure', 'astute', 'spotless', 'precise', 'shrewd', 'careful', 'spruce', 'distinct', 'goody', 'organzied', 'resourceful', 'unadulterated', 'orderly', 'super', 'formidable', 'trim', 'curious', 'rigorous', 'ordered', 'good-looking', 'kiln-dried', 'nice-looking', 'delightful', 'poggers', 'systematic', 'epic', 'enthralling', 'fabulous', 'presentable', 'pleasing', 'splendid']
  await message.channel.send(f'Aren\'t numbers so ' + random_adjective[random.randrange(0, len(random_adjective) - 1)] + '?')

async def update_ses(entry, update_message):
  db[entry] = update_message

async def add_emoji(message, emoji_name):
  for emoji in bot.emojis:
    if emoji.name == emoji_name:
      await message.add_reaction(emoji)

async def send_gif(term, limit):
  # set the apikey and limit
  apikey = os.environ['gif_key']  # test value

  # get the top <limit> GIFs for the search term
  r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (term, apikey, limit))

  if r.status_code == 200:
      # load the GIFs using the urls for the smaller GIF sizes
      top_gifs = json.loads(r.content)['results']
      rand_url = top_gifs[random.randrange(0, limit - 1)]['url']
      return rand_url
  else:
      return None

@tasks.loop(minutes=1)
async def daily_message():
  # channel = discord.get_channel(604834176645988354) # chats and bants
  channel = bot.get_channel(887682725375528963) # testing chat
  await channel.send("Good morning.")

  # send today in history
  # API docs: https://history.muffinlabs.com/
  today = date.today().strftime("%m/%d/%y").split("/")
  month = today[0]
  day = today[1]
  fact_request = requests.get("http://history.muffinlabs.com/date/%s/%s" % (month, day)).json()["data"]

  event_fact = fact_request["Events"][0]
  event_links = " | ".join(["<" + link['link'] + ">" for link in event_fact['links']])
  birth_fact = fact_request['Births'][0]
  birth_links = " | ".join(["<" + link['link'] + ">" for link in birth_fact['links']])
  death_fact = fact_request["Deaths"][0]
  death_links = " | ".join(["<" + link['link'] + ">" for link in death_fact['links']])

  await channel.send("TODAY IN HISTORY: \n")
  await channel.send("\N{bullet} %s: %s \n" % (event_fact['year'], event_fact['text']))
  await channel.send(event_links)
  await channel.send("\N{bullet} %s is born. %s" % (birth_fact['text'], birth_links))
  await channel.send("\N{bullet} %s dies. %s" % (death_fact['text'], death_links))

  # send quote of the day
  # API docs: https://github.com/lukePeavey/quotable
  quote_response = requests.get("https://api.quotable.io/random").json()
  quote = quote_response['content']
  author = quote_response['author']
  await channel.send("QUOTE OF THE DAY: \"%s\" \n~%s" % (quote, author))

  # send definition of the day
  url = "https://wordsapiv1.p.rapidapi.com/words/"
  querystring = {"random":"true"}
  headers = {
    'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
    'x-rapidapi-key': "fb731cefd2msh69364977b49898ep16b903jsn21c4ae1a6eab"
  }
  r = requests.request("GET", url, headers=headers, params=querystring).json()

  word = "\N{bullet}".join([syllable for syllable in r['syllables']['list']]) # join syllables over dot like google definition
  pronunciation = r['pronunciation']['all']
  definitions = "\n\N{bullet}".join([definition['definition'] for definition in r['results']])

  await channel.send("WORD OF THE DAY: %s" % word)
  await channel.send(pronunciation)
  await channel.send("\N{bullet}" + definitions)

@daily_message.before_loop
async def before_daily_message():
  hour = 18
  minute = 55
  await bot.wait_until_ready()
  now = datetime.now()
  future = datetime.datetime(now.year, now.month, now.day, hour, minute)
  if now.hour >= hour and now.minute > minute:
      future += timedelta(days=1)
  await asyncio.sleep((future-now).seconds)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone"))
    # daily_message.start()

# keep_alive() 

bot.add_cog(Music(bot))
bot.add_cog(Text(bot))
bot.run(bot_token)