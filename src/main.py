import globals as gl
import discord
import sys
import os
from replit import db
from Music import Music
from Text import Text
from Memes import Memes
from Requests import Requests
from Schedule import Schedule
from Dice import Dice
from Poll import Poll
from ROR2 import ROR2
from Positivity import Positivity
from Emotes import Emotes
from Miscellaneous import Miscellaneous
from Words import Words
from Images import Images
from Bartender import Bartender
from Ses import Ses
from Math import Math
from keep_alive import keep_alive

bot = gl.bot

async def setup(bot):
  await bot.add_cog(Music(bot))
  await bot.add_cog(Text(bot))
  await bot.add_cog(Memes(bot))
  await bot.add_cog(Requests(bot))
  await bot.add_cog(Schedule(bot))
  await bot.add_cog(Dice(bot))
  await bot.add_cog(Poll(bot))
  await bot.add_cog(ROR2(bot))
  await bot.add_cog(Positivity(bot))
  await bot.add_cog(Emotes(bot))
  await bot.add_cog(Miscellaneous(bot))
  await bot.add_cog(Words(bot))
  await bot.add_cog(Images(bot))
  await bot.add_cog(Bartender(bot))
  await bot.add_cog(Ses(bot))
  await bot.add_cog(Math(bot))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="with consciousness"))
    await setup(bot)

if 'bot_token' in os.environ:
  keep_alive() 
  
try:
  bot.run(gl.bot_token)
  # keys = db.keys()
  # print(keys)
  
  # for guild in bot.guilds:
  #     for channel in guild.channels:
  #       if guild.name:
  #         print(guild.name)
  #       if channel.name:
  #         print(channel.name) 
  #       if channel.category:
  #         print(channel.category.type)
except Exception as e:
  print("ERROR OCCURED WHILE RUNNING: ")
  print("\n")
  print(e)
  print("\n")
  sys.exit()