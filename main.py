import asyncio
import discord
import os
import queue
import requests
import random
from discord.ext import commands
from keep_alive import keep_alive

# bot_token = os.environ['bot_token']
bot_token = os.environ['dbot_token'] # dev bot token
unsplash_token = os.environ['unsplash_key']

import youtube_dl

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

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example')
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
  
  q = queue.Queue()
  song_playing = False

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

  @commands.command()
  async def play(self, ctx, *, url):
    await ctx.invoke(self.bot.get_command('join'))

    """Streams from a url (same as yt, but doesn't predownload)"""

    async with ctx.typing():
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      # self.q.put(player)

      ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

      await ctx.send(f'Now playing: {player.title}')

  def dequeue(self, vc):
    vc.play(self.q.get(), after=lambda e: print('Player error: %s' % e) if e else None)


class Text(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @bot.event
  async def on_message(message):
    await bot.process_commands(message)
    # print(message)
    if message.author == bot.user:
      return

    # hardly knew her
    if message.content.endswith('er') or message.content.endswith('er?') and not message.content.startswith('http'):
      last = (message.content.split()[-1]).replace("?", "")
      await message.channel.send(last + "? I 'ardly knew 'er!")

    # random autism fact
    if '37' in message.content and not message.content.startswith('http'):
      await random_autism(message)

  @bot.event
  async def on_message_edit(before, after):
    # add edit emoji to edited messages
    if not before.content.startswith('http'):
      for emoji in bot.emojis:
        if emoji.name == "edited":
            await after.add_reaction(emoji)
    return # exit if not found

  @commands.command()
  async def die(self, ctx):
    # !die command
    async with ctx.typing():
      await ctx.send("I'd rather die standing than live kneeling")
      await ctx.send("And I don't even have legs")

  @commands.command()
  async def help(self, ctx):
    await ctx.send(
      """```!play <url>: plays YouTube video from given url. Must be in a voice chat
!play <query>: searches and plays YouTube audio with given query. Must be in a voice chat
!join: have a friend join you in voice chat
!ses: Gives the time, date, and location of the next ses
!nature <query>: fetches image related to query
!help: Show this message```""")

  @commands.command()
  async def ses(self, ctx):
    async with ctx.typing():
      message = ctx.message
      for emoji in bot.emojis:
        if emoji.name == "ses":
            await message.add_reaction(emoji)
      await ctx.send("Next Eberron ses is at 6:30pm on September 16th, held online")
  
  @commands.command()
  async def nature(self, ctx, *, query):
    image = requests.get(f'https://api.unsplash.com/photos/random?query=' + query + '&client_id=' + unsplash_token).json()['urls']['full']
    await ctx.send(image)

async def random_autism(message):
  random_decorator = ["trivia", "math", "date", "year"]
  response = requests.get(f'http://numbersapi.com/random/' + random_decorator[random.randrange(0, len(random_decorator) - 1)] + '?json').json()['text']
  await message.channel.send(response)
  random_adjective = ['tidy', 'nifty', 'good', 'great', 'cool', 'elegant', 'dandy', 'tasteful', 'groovy', 'clean', 'peachy', 'keen', 'refined', 'adroit', 'straight', 'corking', 'smashing', 'bully', 'swell', 'cracking', 'undiluted', 'bang-up', 'full-strength', 'not bad', 'slap-up', 'nice', 'lovely', 'clever', 'wonderful', 'fantastic', 'wondrous', 'stunning', 'classy', 'awesome', 'amazing', 'interesting', 'beautiful', 'brilliant', 'terrific', 'cute', 'simple', 'fun', 'gorgeous', 'groovin', 'snazzy', 'crisp', 'spiffy', 'crafty', 'fancy', 'ingenious', 'sweet', 'pretty', 'skilful', 'purty', 'wow', 'handsome', 'fine', 'well', 'chic', 'flawless', 'shipshape', 'leggy', 'clear', 'impeccable', 'pure', 'astute', 'trig', 'spotless', 'precise', 'shrewd', 'careful', 'spruce', 'distinct', 'goody', 'resourceful', 'unadulterated', 'orderly', 'own', 'super', 'formidable', 'trim', 'net', 'unmixed', 'dry', 'extra', 'bandbox', 'near', 'rigorous', 'sec', 'belle', 'sect', 'sce', 'esa', 'owl', 'ordered', 'good-looking', 'kiln-dried', 'nice-looking', 'ces', 'delightful', 'poggers', 'epic', 'fabulous', 'presentable', 'splendid']
  await message.channel.send(f'Aren\'t numbers so ' + random_adjective[random.randrange(0, len(random_adjective) - 1)] + '?')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

# keep_alive() 

bot.add_cog(Music(bot))
bot.add_cog(Text(bot))
bot.run(bot_token)