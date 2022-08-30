import requests
import globals as gl
import math
from replit import db
from discord.ext import commands

class Memes(commands.Cog):
  # commands associated with memes
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command(aliases=['lennies'])
  async def lenny(self, ctx, num=1):
    if num > 500:
      await ctx.send("Error 37: lenny overflow")
      return
    if num > 100:
      await ctx.send(gl.straining_gif)
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
    pun = requests.get("https://dad-jokes.p.rapidapi.com/random/joke?rapidapi-key=%s" % (gl.rapid_api)).json()
    print(pun)
    if pun['success']:
      async with ctx.typing():
        pun = pun['body'][0]
        if pun['NSFW']:
          await ctx.send("Oh, this one's a nasty one.")

        await ctx.send(pun['setup'])

        def check(m):
          return m.channel == ctx.channel

        await gl.bot.wait_for('message', check=check)
        await ctx.send(pun['punchline'])

  @commands.command()
  async def meme(self, ctx):
    r = requests.get("https://meme-api.herokuapp.com/gimme").json()
    await ctx.send(r['title'])
    await ctx.send(r['url'])

  @commands.command()
  async def ladder(self, ctx):
    return await ctx.send("https://i.ibb.co/M9rz8r7/ladders.webp")