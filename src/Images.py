from discord.ext import commands
import globals as gl
import discord
from PIL import Image

class Emotes(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None


	@commands.command()
	async def smoosh(self, ctx, emoji1, emoji2):
    filename = "docs/assets/biglaff.png"
    img = Image.open(filename)
    width, height = img.size

    area = (0, 0, width/2, height/2)
    img = img.crop(area)
          
    return await ctx.send(img)

    
