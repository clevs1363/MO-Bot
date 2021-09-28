import asyncio
import discord
import os
import requests
import random
import youtube_dl
import json
import math
from datetime import date, datetime, timedelta
from pytz import timezone
from discord.ext import commands, tasks
from keep_alive import keep_alive
from pprint import pprint
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
my_user_id = int(os.environ['my_user_id'])

# gif links
no_gif = "https://tenor.com/view/no-i-dont-think-i-will-captain-america-old-capt-gif-17162888"
straining_gif = "https://tenor.com/view/straining-gif-6190466"
finger_wag = "https://tenor.com/view/nope-no-shake-finger-shake-finger-gif-4138495"
annoyed = "https://tenor.com/view/kabangu-upset-annoyed-gif-14814728"

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
  
  @commands.command()
  async def pause(self, ctx):
    """Pause the currently playing song."""
    vc = ctx.voice_client

    if not vc or not vc.is_playing():
      embed = discord.Embed(title="", description="I am currently not playing anything", color=discord.Color.dark_green())
      return await ctx.send(embed=embed)
    elif vc.is_paused():
      return

    vc.pause()
    await ctx.send("Paused ⏸️")
  
  @commands.command()
  async def resume(self, ctx):
    """Resume the currently paused song."""
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
      embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.dark_green())
      return await ctx.send(embed=embed)
    elif not vc.is_paused():
      return

    vc.resume()
    await ctx.send("Resuming ⏯️")
  
  @commands.command(name='skip', description="skips to next song in queue")
  async def skip(self, ctx):
    """Skip the song."""
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
      embed = discord.Embed(title="", description="I'm not connected to a voice channel", color=discord.Color.dark_green())
      return await ctx.send(embed=embed)

    if vc.is_paused():
      pass
    elif not vc.is_playing():
      return
    
    if self.songs.empty():
      return await ctx.send("No other songs in queue. Skip ignored")

    await ctx.send("Skipping song...")
    vc.stop()

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
    
    if isinstance(message.channel, discord.DMChannel):
      if message.author.id != my_user_id:
        me = bot.get_user(547127905679966209) # my id
        await me.send(f"*Message from {message.author}*:\n{message.content}")

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
  
  @bot.event
  async def on_reaction_add(reaction, user):
    if reaction.count == 5 and reaction.emoji.name == "biglaff" and reaction.message.author.name == "Obotma":
      await reaction.message.reply("https://tenor.com/view/drop-the-mic-obama-mic-drop-gif-13109295")

  # 
  # <-- COMMANDS -->
  #

  @commands.command()
  async def test_emoji(self, ctx):
    with open(r"docs/assets/Maleakosbadtrip.gif", "rb") as img:
      img_byte = img.read()
      await ctx.message.guild.create_custom_emoji(name = ("maleakos"), image = img_byte)
  
  @commands.command()
  async def test_emoji_react(self, ctx):
    for emoji in ctx.guild.emojis():
      if emoji.name == "maleakos":
        ctx.message_add_reaction(emoji)
  
  @commands.command()
  async def help(self, ctx):
    embed = discord.Embed(
    title = "Obotma Commands",
    description = "A fun passion project for the boys. It started as a replacement to Groovy and Rhythm, and has evolved into a collection of random commands for the server. \n\n https://clevs1363.github.io/Obotma/",
    color = discord.Color.dark_blue()
    )
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
    await ctx.send(embed=embed)

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
  async def nature(self, ctx, *query):
    if query:
      image = requests.get(f'https://api.unsplash.com/photos/random?query=' + query[0] + '&client_id=' + unsplash_token).json()['urls']['regular']
    else:
      image = requests.get(f'https://api.unsplash.com/photos/random?client_id=' + unsplash_token).json()['urls']['regular']
    await ctx.send(image)

  @commands.command()
  async def ses(self, ctx, *msg):
    async with ctx.typing():
      await add_emoji(ctx.message, 'ses')
      if msg: # check if arguments were passed
        if ctx.author.id == my_user_id:
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
      if ctx.author.name == "Ś̶̨h̸̥͌r̷̬̍ö̷͉o̴̡͐m̶̧̏b̴̳̆o̵̎͜" or ctx.author.id == my_user_id:
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
    if ctx.message.author.id == my_user_id:
      async with ctx.typing():
        await ctx.send("New features added! Check !help for help")
  
  @commands.command()
  async def scan(self, ctx):
    async with ctx.typing():
      if ctx.message.author.id == my_user_id:   
        reactions_given = {}
        reactions_received = {}
        # example dictionary format
        # {
        #   CerealGuy69: {
        #     biglaff: 50,
        #     ses: 100
        #   }, Little_G: {
        #     biglaff: 100,
        #     ses: 50
        #   } 
        # }
        async for msg in ctx.channel.history(limit=50000):
          for reaction in msg.reactions:
            # analyze reactions received
            author = msg.author.name
            # make sure emoji isnt a string, and assign to variable for simplicity
            if not isinstance(reaction.emoji, str):
              emoji = reaction.emoji.name
            else:
              continue
            if author in reactions_received:
              # user already in 
              if emoji in reactions_received[author]:
                # user already has been reacted to with this emote, add to total
                reactions_received[author][emoji] += reaction.count
              else:
                # emote not documented, initialize to total
                reactions_received[author][emoji] = reaction.count
            else:
              # user not yet in reactions, initialize to emoji count
              reactions_received[author] = {emoji: reaction.count}

            # analyze reactions given
            async for reactor in reaction.users():
              if reactor.name in reactions_given:
                # user already reacted
                if emoji in reactions_given[reactor.name]:
                  # user already reacted with specific emoji
                  reactions_given[reactor.name][emoji] += 1
                else:
                  # reactor has not yet reacted with specific emoji
                  reactions_given[reactor.name][emoji] = 1
              else:
                # reactor has not yet reacted
                reactions_given[reactor.name] = {emoji: 1}

        # --Create Embeds--

        # map emoji names to their id's
        emojis = {}
        for emoji in ctx.guild.emojis:
          emojis[emoji.name] = emoji.id

        # create receieved emojis stat embed      
        await self.create_embed(emojis, reactions_received, "received", ctx)
        
        # create given emojis stat embed
        await self.create_embed(emojis, reactions_given, "given", ctx)

      else:
        await ctx.send("We know we'd break the damn bot with everyone scanning")
        return await ctx.send(finger_wag)
    
  async def create_embed(self, emojis, data, given_or_received, ctx):
    # same code for creating given and received emotes
    for user in data:
      embed = discord.Embed(
        title = "Emotes " + given_or_received.capitalize() + " Stats",
        description = "Amount of emotes " + given_or_received + " for " + user + " in " + str(ctx.channel.name),
        color = discord.Color.dark_green()
      )
      # get user avatar
      avatar = "https://www.biography.com/.image/t_share/MTE4MDAzNDEwNzg5ODI4MTEw/barack-obama-12782369-1-402.jpg" # default to Obama
      for member in ctx.guild.members:
        if member.name == user:
          avatar = member.avatar_url
      embed.set_author(name=user, icon_url=avatar)
      for emote in data[user]:
        emoji_string = "<" + ":" + emote + ":" + str(emojis[emote]) + ">"
        embed.add_field(name = emoji_string, value = data[user][emote])
      await ctx.send(embed=embed)

class Memes(commands.Cog):
  # commands associated with memes
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

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
  async def meme(self, ctx):
    r = requests.get("https://meme-api.herokuapp.com/gimme").json()
    await ctx.send(r['title'])
    await ctx.send(r['url'])

  @commands.command()
  async def request(self, ctx, *req):
    if req:
      if 'requests' in db.keys() and len(db['requests']) > 14:
        await ctx.send(annoyed)
        return
      # add request to dictionary
      if 'requests' in db.keys():
        db['requests'][" ".join(req)] = ctx.message.author.name
      else:
        db['requests'] = {" ".join(req): ctx.message.author.name}
      await add_emoji(ctx.message, "pepehap")
      await ctx.send("\U0001F60E" + "\U0001F44D")
      await ctx.send("You are number %s in the queue" % (len(db['requests'])))
    else:
      if 'requests' in db.keys():
        # list requests
        ret_string = ""
        counter = 1
        for item in db['requests'].keys():
          ret_string += str(counter) + '. ' + item + '\n'
          counter += 1
        await ctx.send(ret_string)
      else:
        # requests are empty
        await ctx.send("No features requested yet") 
  
  @commands.command()
  async def delete_request(self, ctx, num):
    if int(num) == 0 and ctx.message.author.id == my_user_id:
      # clear list
      if 'requests' in db:
        del db["requests"]
        await ctx.send("admin yoink")
      else:
        await ctx.send('nothing to admin yoink')
      return
    if 'request' in db:
      counter = 1
      for request in db['requests'].keys():
        if counter == int(num):
          if ctx.message.author.name == db['requests'][request] or ctx.message.author.id == my_user_id:
            db['requests'].pop(request)
            await ctx.send("yoink")
          else:
            await ctx.send("Not very cash money of you to try and delete someone else's request")
            await ctx.send(finger_wag)
        counter += 1
    else:
      await ctx.send('nothing to yoink yet')

class Schedule(commands.Cog):
  # commands and functions that occur at scheduled times
  def __init__(self, bot):
    self.bot = bot
    self.daily_message.start()

  @tasks.loop(hours=24)
  async def daily_message(self):
    channel = bot.get_channel(604834176645988354) # chats and bants
    # channel = bot.get_channel(887682725375528963) # testing chat
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

    # API is very inconsistent, loop until getting a valid word
    all_fields = False
    while not all_fields:
      r = requests.request("GET", url, headers=headers, params=querystring).json()
      if 'word' not in r or 'results' not in r:
        pass
      else:
        all_fields = True

    try:
      word = "\N{bullet}".join([syllable for syllable in r['syllables']['list']]) # join syllables over dot like google definition
    except:
      word = r['word'] # revert to default word if syllables not present
    pronunciation = "[none]"
    if r['pronunciation']:
      pronunciation = r['pronunciation']['all']
    definitions = "\n\N{bullet}".join([definition['definition'] for definition in r['results']])

    await channel.send("WORD OF THE DAY: %s" % word)
    await channel.send(pronunciation)
    await channel.send("\N{bullet}" + definitions)

  @daily_message.before_loop
  async def before_daily_message(self):
    hour = 7
    minute = 30
    await bot.wait_until_ready()
    tz = timezone('EST')
    now = datetime.now(tz) 
    future = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    await asyncio.sleep((future-now).seconds)

class Dice(commands.Cog):
  # commands associated with the built-in dice roller
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command()
  async def r(self, ctx, roll):
    if roll == "stats":
      stats = await self.roll_stats()
      await ctx.send(", ".join([str(stat) for stat in stats]))
      total = sum(stats)
      if total > 75:
        await ctx.send("Damn. I like ya stats, g")
      elif total < 75 and total > 69:
        await ctx.send("*light applause*")
      else:
        await ctx.send("https://i.ibb.co/KWK4Ysk/badroll.jpg")
      return
    try:
      if roll.startswith("d"):
        # interpet as one dice
        num = 1
        dice = roll[1:]
      else:
        data = roll.split("d")
        num = int(data[0])
        dice = data[1]
      mods_raw = dice.split("+")
      if len(mods_raw) == 1:
        # no modifiers
        mods = 0
      else:
        mods = int(mods_raw[1])
      dice = int(mods_raw[0]) # dice will always be first element
      result = ""
      total = 0
      for res in range(num):
        rolled = random.randrange(1, dice+1)
        total += rolled
        result += str(rolled) + ", "
      total += mods
      if total - mods == 20 and num == 1 and dice == 20: # only trigger on nat 1d20
        await ctx.send('https://ih1.redbubble.net/image.756099120.1069/st,small,507x507-pad,600x600,f8f8f8.u2.jpg')
      elif total - mods == 1 and num == 1 and dice == 20:
        await ctx.send('https://ih1.redbubble.net/image.1047087046.0562/st,small,845x845-pad,1000x1000,f8f8f8.u1.jpg')
      else:
        await ctx.send(result[:-2]) # sliced to remove last ', '
      if mods != 0:
        await ctx.send("Total = " + str(total))
    except Exception as e:
      print(e)
      await ctx.send("Error: dice fell off the table. Reformat and try again")
  
  async def roll_stats(self):
    stats = []
    for roll in range(6):
      drop_lowest = [random.randrange(1, 7) for x in range(4)]
      drop_lowest.remove(min(drop_lowest))
      stats.append(sum(drop_lowest))
    return stats

class Poll(commands.Cog):
  # commands associated with the built-in poll function
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
  
  @commands.command()
  async def poll(self, ctx, *, args):
    try:
      # get the title
      poll_title = args[args.find('{') + 1:args.find('}')]
      args = args[args.find('['):]

      # get the arguments
      options = []
      while args:
        options.append(args[args.find('[') + 1:args.find(']')])
        args = args[args.find(']') + 2:] # +2 to account for bracket and white space
      
      # create embed
      embed = discord.Embed(
        title = poll_title,
        description = "React with emotes below to vote!",
        color = discord.Color.dark_green()
      )
      embed.set_author(name="Barack Obama", icon_url= "https://www.biography.com/.image/t_share/MTE4MDAzNDEwNzg5ODI4MTEw/barack-obama-12782369-1-402.jpg")
      counter = 1
      # await ctx.send("0\N{combining enclosing keycap}")
      for option in options:
        emoji_string = str(counter) + "\N{combining enclosing keycap}"
        embed.add_field(name = "Option " + emoji_string + ":", value = option, inline="False")
        counter += 1
      size = len(options)
      # check if poll only has 1 option to give snark
      if size == 1:
        embed.add_field(name = "Option 2\N{combining enclosing keycap}:", value = "Pollmaker is gey", inline="False")
      msg = await ctx.send(embed=embed)
      # add emojis
      for x in range(size):
        # x + 1 because it starts counting at 0
        emoji_string = str(x+1) + "\N{combining enclosing keycap}"
        await msg.add_reaction(emoji_string)
      if size == 1:
        await msg.add_reaction("2\N{combining enclosing keycap}")
      return
    except:
      await ctx.send("Poll was rigged. Reformat and try again")
      return
  
class ROR2(commands.Cog):
  # commands associated with ror2 and swaggin
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.swag_id = 0
    self.swaggers = []
    self.characters = ['Acrid', 'Artificer', 'Bandit', 'Captain', 'Commando', 'Engineer', 'Huntress', 'Loader', 'Mercenary', 'MUL-T', 'REX'] 
    self.artifacts = {
      'Chaos': 'Friendly fire is enabled for both survivors and monsters alike.', 
      'Command': 'Choose your items.', 
      'Death': 'When one player dies, everyone dies. Enable only if you want to truly put your teamwork and individual skill to the ultimate test.', 
      'Dissonance': 'Monsters can appear outside their usual environments.',
      'Enigma': 'Spawn with a random equipment that changes every time it\'s activated.',
      'Evolution': 'Monsters gain items between stages.',
      'Frailty': 'Fall damage is doubled and lethal.',
      'Glass': 'Allies deal 500% damage, but have 10% health.',
      'Honor': 'Enemies can only spawn as elites.',
      'Kin': 'Monsters will be of only one type per stage.',
      'Metamorphosis': 'Players always spawn as a random survivor.',
      'Sacrifice': 'Monsters drop items on death, but Chests no longer spawn.',
      'Soul': 'Wisps emerge from defeated monsters.',
      'Spite': 'Enemies drop multiple exploding bombs on death.',
      'Swarms': 'Monster spawns are doubled, but monster maximum health is halved.',
      'Vengeance': 'Your relentless doppelganger will invade every 10 minutes.'
    }
  
  @commands.command()
  async def swag(self, ctx, *swag_time):
    if not swag_time:
      return await ctx.send("Provide a time (!swag <time>)")
    else:
      t = str(swag_time[0])
      self.swaggers = []
      embed = discord.Embed(
        title = "Swag at " + str(t) +"?",
        description = "React yes or no below",
        color = discord.Color.dark_blue()
      )
      embed.set_author(name="Risk of Rain 2", icon_url= "https://www.gamespot.com/a/uploads/original/1575/15759911/3719483-risk-of-rain-2-review-promothumb.jpg")
      embed.add_field(name = "Yes:", value = "\N{thumbs up sign}")
      embed.add_field(name = "No:", value = "\N{thumbs down sign}")

      # get ror2 role id
      role = 0
      for role in ctx.guild.roles:
        if role.name == "ror2":
          role_id = role.id
      await ctx.send("<@&" + str(role_id) + ">")
      msg = await ctx.send(embed=embed)
      await msg.add_reaction("\N{thumbs up sign}")
      await msg.add_reaction("\N{thumbs down sign}")
      self.swag_id = msg.id
      return
  
  @commands.command()
  async def swaggers(self, ctx):
    if self.swaggers:
      await ctx.send("Current swaggers: ")
      await ctx.send(" ".join(self.swaggers))
    else:
      await ctx.send("No swaggers yet. Use !swag to initiate a potential swag. Will remove previous swagger session")
      await ctx.send("https://i.ibb.co/f1fwZRf/john-travolta-lost-ror2.gif")
  
  @commands.command()
  async def random_swag(self, ctx, *num):
    for swagger in self.swaggers:
      await ctx.send(swagger + ": " + random.choice(self.characters))
    if num:
      num = int(num[0])
      if num <= 16 and num >= 0:
        chosen_artifacts = []
        for artifact in range(num):
          # ensure every addition is unique
          unique = False
          while not unique:
            rand_artifact = random.choice(list(self.artifacts.keys()))
            if rand_artifact in chosen_artifacts:
              unique = False
            else:
              chosen_artifacts.append(rand_artifact)
              unique = True
        await ctx.send("Artifacts: " + ", ".join(chosen_artifacts))
      else:
        await ctx.send("Enter a valid number of artifacts between 0 and 16")
        await ctx.send("https://i.ibb.co/f1fwZRf/john-travolta-lost-ror2.gif")
    else:
      await ctx.send("No artifacts selected.")
  
  @commands.command()
  async def artifact(self, ctx, artifact):
    if artifact in self.artifacts:
      await ctx.send(self.artifacts[artifact])
    else:
      await ctx.send("Artifact not found")
      await ctx.send("https://i.ibb.co/f1fwZRf/john-travolta-lost-ror2.gif")

  
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    if not user.name == bot.user and reaction.message.id == self.swag_id and reaction.emoji == "\N{thumbs up sign}":
      self.swaggers.append(user.name)
  
  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction, user):
    if reaction.emoji == "\N{thumbs up sign}":
      self.swaggers.remove(user.name)
    
# --GLOBAL FUNCTIONS--

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone"))

# keep_alive() 

bot.add_cog(Music(bot))
bot.add_cog(Text(bot))
bot.add_cog(Memes(bot))
bot.add_cog(Schedule(bot))
bot.add_cog(Dice(bot))
bot.add_cog(Poll(bot))
bot.add_cog(ROR2(bot))
bot.run(bot_token)