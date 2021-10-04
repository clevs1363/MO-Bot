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

  @commands.command()
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
  async def request(self, ctx, *req):
    if req:
      if 'requests' in db.keys() and len(db['requests']) > 14:
        await ctx.send(gl.annoyed)
        return
      # add request to dictionary
      if 'requests' in db.keys():
        db['requests'][" ".join(req)] = ctx.message.author.name
      else:
        db['requests'] = {" ".join(req): ctx.message.author.name}
      await gl.add_emoji(ctx.message, "pepehap", gl.bot.emojis)
      await ctx.send("\U0001F60E" + "\U0001F44D")
      await ctx.send("You are number %s in the queue" % (len(db['requests'])))
    else:
      if 'requests' in db.keys():
        # list requests
        ret_string = ""
        counter = 1
        for item in db['requests'].keys():
          ret_string += str(counter) + '. ' + item + '\n'
          counter += 1
        await ctx.send(ret_string)
      else:
        # requests are empty
        await ctx.send("No features requested yet. Check the site to see what's in progress")
        await ctx.invoke(self.bot.get_command('help')) 
  
  @commands.command()
  async def delete_request(self, ctx, num):
    if int(num) == 0 and ctx.message.author.id == gl.my_user_id:
      # clear list
      if 'requests' in db:
        del db["requests"]
        await ctx.send("admin yoink")
      else:
        await ctx.send('nothing to admin yoink')
      return
    if 'requests' in db:
      counter = 1
      for request in db['requests'].keys():
        if counter == int(num):
          if ctx.message.author.name == db['requests'][request] or ctx.message.author.id == gl.my_user_id:
            db['requests'].pop(request)
            await ctx.send("yoink")
          else:
            await ctx.send("Not very cash money of you to try and delete someone else's request")
            await ctx.send(gl.finger_wag)
        counter += 1
    else:
      await ctx.send('nothing to yoink yet')