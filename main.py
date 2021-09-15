import asyncio
import discord
import os
from discord.ext import commands
from keep_alive import keep_alive
from discord.utils import get

# bot_token = os.environ['bot_token']
bot_token = os.environ['dbot_token'] # dev bot token

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

  @commands.command()
  async def goeen(self, ctx):
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
  async def plonk(self, ctx, *, url):
    await ctx.invoke(self.bot.get_command('goeen'))

    """Streams from a url (same as yt, but doesn't predownload)"""

    async with ctx.typing():
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

      await ctx.send(f'Now playing: {player.title}')

class Text(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @bot.event
  async def on_message(message):
    # print(message)
    if message.author == bot.user:
      return

    if message.content.endswith('er') or message.content.endswith('er?'):
      await message.channel.send("I 'ardly knew 'er!")

  @bot.event
  async def on_message_edit(before, after):
    # add edit emoji to edited messages
    for emoji in bot.emojis:
      if emoji.name == "edited":
          await after.add_reaction(emoji)
    return # exit if not found

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

# keep_alive() 

bot.add_cog(Music(bot))
bot.add_cog(Text(bot))
bot.run(bot_token)