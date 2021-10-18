import globals as gl
import discord
import sys
import os
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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone"))

if 'bot_token' in os.environ:
  keep_alive() 

bot.add_cog(Music(bot))
bot.add_cog(Text(bot))
bot.add_cog(Memes(bot))
bot.add_cog(Requests(bot))
bot.add_cog(Schedule(bot))
bot.add_cog(Dice(bot))
bot.add_cog(Poll(bot))
bot.add_cog(ROR2(bot))
bot.add_cog(Positivity(bot))
bot.add_cog(Emotes(bot))
bot.add_cog(Miscellaneous(bot))
bot.add_cog(Words(bot))
bot.add_cog(Images(bot))
bot.add_cog(Bartender(bot))
bot.add_cog(Ses(bot))
bot.add_cog(Math(bot))
try:
  bot.run(gl.bot_token)
except Exception as e:
  print("ERROR OCCURED WHILE RUNNING: ")
  print("\n")
  print(e)
  print("\n")
  sys.exit()