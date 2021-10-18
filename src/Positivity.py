import asyncio
import requests
import random
import discord
import globals as gl
from replit import db
from discord.ext import commands

class Positivity(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    if 'thank_stats' not in db.keys():
      db['thank_stats'] = {}
  
  @commands.command()
  async def hug(self, ctx):
    url = await gl.send_gif("hug", 50)
    await ctx.send(url)
  
  @commands.command()
  async def encourage(self, ctx):
    r = requests.get("https://www.affirmations.dev").json()
    affirmation = r['affirmation']
    if affirmation[-1] != '.':
      affirmation += '.'
    await ctx.send(affirmation)
    async with ctx.typing():
        await asyncio.sleep(random.randrange(2, 5))
        await ctx.send("Would you like to hear an inspirational quote?")

    def check(m):
      return m.channel == ctx.channel and ('yes' in m.content.lower() or 'no' in m.content.lower())

    msg = await gl.bot.wait_for('message', check=check, timeout=60)
    if 'yes' in msg.content.lower():
      r = requests.get("https://zenquotes.io/api/random").json()[0]
      await ctx.send("\"" + r['q'] + "\"\n" + "~" + r['a'])
    else:
      await msg.add_reaction("\N{thumbs up sign}")

  @commands.command()
  async def compliment(self, ctx):
    r = requests.get("https://complimentr.com/api").json()
    compliment = r['compliment']
    await ctx.send(ctx.message.author.name + ", " + compliment + ".")

  @commands.command()
  async def nature(self, ctx, *query):
    if query:
      image = requests.get(f'https://api.unsplash.com/photos/random?query=' + query[0] + '&client_id=' + gl.unsplash_token).json()['urls']['regular']
    else:
      image = requests.get(f'https://api.unsplash.com/photos/random?client_id=' + gl.unsplash_token).json()['urls']['regular']
    await ctx.send(image)
  
  @commands.command()
  async def thank(self, ctx): 
    author_id = str(ctx.author.id)
    if author_id in db['thank_stats']:
      db['thank_stats'][author_id] += 1
    else:
      db['thank_stats'][author_id] = 1
    for emoji in ctx.guild.emojis:
      if emoji.name == 'pepepet':
        await ctx.send(emoji)