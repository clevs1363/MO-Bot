from discord.ext import commands
import globals as gl
import discord
import datetime
from PIL import Image

class Bartender(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
  
  @commands.command()
  async def drink(self, ctx, name):
    pass