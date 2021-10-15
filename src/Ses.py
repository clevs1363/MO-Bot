import asyncio
import requests
import random
from replit import db
import globals as gl
from discord.ext import commands

class Ses(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
  
  @commands.command()
  async def ses(self, ctx, *msg):
    async with ctx.typing():
      await gl.add_emoji(ctx.message, 'ses', gl.bot.emojis)
      if msg: # check if arguments were passed
        if ctx.author.id == gl.my_user_id:
          output = " ".join(msg)
          await ctx.message.channel.edit(topic = output)
          await gl.update_ses('ses', output)
          await ctx.send('--SESSION CHANGED--')
        else:
          return await ctx.send(gl.no_gif)
      return await ctx.send(db['ses'])

  @commands.command()
  async def abyses(self, ctx, *msg):
    await gl.add_emoji(ctx.message, 'ses', gl.bot.emojis)
    if msg: # check if arguments passed
      if ctx.author.name == "Ś̶̨h̸̥͌r̷̬̍ö̷͉o̴̡͐m̶̧̏b̴̳̆o̵̎͜" or ctx.author.id == gl.my_user_id:
        output = " ".join(msg)
        await ctx.message.channel.edit(topic = output)
        await gl.update_ses('abyses', output)
        await ctx.send('--SESSION CHANGED--')
      else:
        await ctx.send(gl.no_gif)
        return
    await ctx.send(db['abyses'])
  
  