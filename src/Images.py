from discord.ext import commands
import globals as gl
import discord
from io import BytesIO
from PIL import Image
from subprocess import Popen, PIPE

class Images(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command()
  async def smoosh(self, ctx, emoji1, emoji2):
    # get first emoji
    c1 = None
    for emoji in ctx.guild.emojis:
      if emoji.name == emoji1:
        c1 = await emoji.url.read()
    img = Image.open(BytesIO(c1), mode='r')
    width, height = img.size
    area = (0, 0, width/2, height)
    img = img.crop(area) # cut in left half

    # get second emoji
    c2 = None
    for emoji in ctx.guild.emojis:
      if emoji.name == emoji2:
        c2 = await emoji.url.read()
    img2 = Image.open(BytesIO(c2), mode='r')
    img2 = img2.resize((width, height)) # make sure they're the same size
    width2, height2 = img2.size

    area2 = (width2/2, 0, width2, height2)
    img2 = img2.crop(area2)
    print(img2.mode)
    print(img2.size)

    # copy into new image
    dst = Image.new('RGBA', (img.width + img2.width, img.height))
    dst.paste(img, (0, 0))
    dst.paste(img2, (img.width, 0))

    # convert into sendable object
    b = BytesIO()
    dst.save(b, "PNG")
    b.seek(0)
  
    return await ctx.send(file=discord.File(b, filename='smooshed.png'))

    
