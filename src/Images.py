from discord.ext import commands
import globals as gl
import discord
from io import BytesIO
from PIL import Image
from subprocess import Popen, PIPE
import re

class Images(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command()
  async def smoosh(self, ctx, emoji1, emoji2):
    # get first emoji
    emoji1 = re.sub("[0-9]{18}", "", emoji1).replace(":", "").replace("<", "").replace(">", "")
    emoji2 = re.sub("[0-9]{18}", "", emoji2).replace(":", "").replace("<", "").replace(">", "")
    e1 = None
    for emoji in ctx.guild.emojis:
      if emoji.name == emoji1:
        e1 = await emoji.url.read()
    if not e1:
      return await ctx.send("Emoji 1 not found :(")
    img = Image.open(BytesIO(e1), mode='r')
    width, height = img.size
    area = (0, 0, width/2, height)
    img = img.crop(area) # cut in left half

    # get second emoji
    e2 = None
    for emoji in ctx.guild.emojis:
      if emoji.name == emoji2:
        e2 = await emoji.url.read()
    if not e2:
      return await ctx.send("Emoji 2 not found :(")
    img2 = Image.open(BytesIO(e2), mode='r')
    img2 = img2.resize((width, height)) # make sure they're the same size
    width2, height2 = img2.size

    area2 = (width2/2, 0, width2, height2)
    img2 = img2.crop(area2)

    # copy into new image
    dst = Image.new('RGBA', (img.width + img2.width, img.height))
    dst.paste(img, (0, 0))
    dst.paste(img2, (img.width, 0))

    # convert into sendable object
    b = BytesIO()
    dst.save(b, "PNG")
    b.seek(0)
  
    return await ctx.send(file=discord.File(b, filename='smooshed.png'))

    
