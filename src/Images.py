from discord.ext import commands
import globals as gl
import discord
from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from subprocess import Popen, PIPE
import re
import emojis as emj
import math

class Images(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command(aliases = ['pfp', 'profile_picture'])
  async def profile(self, ctx, *username):
    if not username:
      raw = await ctx.author.avatar_url.read()
      img = Image.open(BytesIO(raw), mode='r')
      b = BytesIO()
      img.save(b, "PNG")
      b.seek(0)
      return await ctx.send(file=discord.File(b, filename='profile.png'))
    else:
      username = " ".join(username)
      for user in ctx.guild.members:
        if user.nick == username or user.name == username:
          raw = await user.avatar_url.read()
          img = Image.open(BytesIO(raw), mode='r')
          b = BytesIO()
          img.save(b, "PNG")
          b.seek(0)
          return await ctx.send(file=discord.File(b, filename='profile.png'))
      return await ctx.send("User not found")
  
  @commands.command(aliases = ['smooshy'])
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

    if ctx.invoked_with == 'smooshy':
      area = (0, 0, width, height/2)
      img = img.crop(area) # cut in top half

      area2 = (0, height/2, width2, height2)
      img2 = img2.crop(area2)

      # copy into new image
      dst = Image.new('RGBA', (img.width + img2.width, img.height + img2.height))
      dst.paste(img, (0, 0))
      dst.paste(img2, (0, img.height))
    else:
      area = (0, 0, width/2, height)
      img = img.crop(area) # cut in left half

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
  
  @commands.command(aliases=['dei'])
  async def default_emoji_img(self, ctx, emoji):
    img = Image.open(BytesIO(emj.encode(emoji)), mode='r')
    await ctx.send(file=discord.File(BytesIO(img.tobytes()), filename='dei.png'))
  
  # @commands.command()
  # async def img_to_text(self, ctx):
  #   b = await ctx.message.attachments[0].read()
  #   b = BytesIO(b)
  #   img = Image.open(b)
  #   txt = pytesseract.image_to_string(img)
  #   await ctx.send(txt)

  @commands.command(aliases=['fq'])
  async def farquaad(self, ctx, text):
    img = Image.open("docs/assets/fq.png")
    final_img = await self.text_to_image(img, text)
    return await ctx.send(file=discord.File(final_img, filename='farquaad.png'))

  @commands.command()
  async def no(self, ctx, text):
    img = Image.open("docs/assets/no.png")
    final_img = await self.text_to_image(img, "no " + text)
    return await ctx.send(file=discord.File(final_img, filename='no.png'))

  @commands.command()
  async def sens(self, ctx, text):
    em = None
    for guild in ctx.guilds:
      for emoji in ctx.guild.emojis:
        if emoji.name == "sens":
          em = await emoji.url.read()
    if em:
      img = Image.open(BytesIO(em), mode='r')
      I1 = ImageDraw.Draw(img)
      font = ImageFont.truetype('docs/assets/impact.ttf', 30)
      I1.text((50, 50), text, font=font, fill=(255, 255, 255))

      # copy into new image
      dst = Image.new('RGBA', (img.width, img.height))
      dst.paste(img, (0, 0))
  
      # convert into sendable object
      b = BytesIO()
      dst.save(b, "PNG")
      b.seek(0)
      return await ctx.send(file=discord.File(b, filename='sens_' + text + '.png'))
      

  async def text_to_image(self, img, text):
    text = text.upper()
    width, height = img.size
    I1 = ImageDraw.Draw(img)
    font_size = math.floor((width * height) / 16000) # guesstimate
    font = ImageFont.truetype('docs/assets/impact.ttf', font_size)
    text_width, text_height = I1.textsize(text)
    # print(text_width)
    print(width)
    print(text_width)
    x = (width-(text_width*len(text)))/2
    print(x)
    y = height-(height/5)
    I1.text((x-4, y-4), text, font=font, fill="black")
    I1.text((x+4, y-4), text, font=font, fill="black")
    I1.text((x-4, y-4), text, font=font, fill="black")
    I1.text((x+4, y+4), text, font=font, fill="black")
    I1.text((x, y), text, font=font, fill=(255, 255, 255))

    # copy into new image
    dst = Image.new('RGBA', (img.width, img.height))
    dst.paste(img, (0, 0))

    # convert into sendable object
    b = BytesIO()
    dst.save(b, "PNG")
    b.seek(0)
    return b
  