import youtube_dl
import discord
import asyncio
from discord.ext import commands

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
    self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

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