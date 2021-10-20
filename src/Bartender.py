from discord.ext import commands, tasks
from replit import db
from datetime import datetime
import pytz as tz
import globals as gl
import requests
import random
import asyncio

class Bartender(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    # set timer to say something at 5:00pm
    self.happy_hour = False
    self.bar_open.start()
    self.bar_close.start()
    if 'drink_stats' not in db.keys():
      db['drink_stats'] = {}
  
  @commands.command()
  async def drink(self, ctx, *name):
    name = "%20".join(name)
    if not self.happy_hour:
      return await ctx.send("Sorry, friend. Come back at 5pm when we're open.  Feel free to take some complimentary `!coffee`.")
    await self.add_stat(ctx.author.id)
    # get drink image by name
    return await ctx.invoke(self.bot.get_command('nature'), (name))
  
  @commands.command()
  async def cocktail(self, ctx, *name):
    if not self.happy_hour:
      return await ctx.send("Sorry, friend. Come back at 5pm when we're open.  Feel free to take some complimentary `!coffee`.")
    await self.add_stat(ctx.author.id)
    alcoholic = "Non_Alcoholic" if "non-alcoholic" in name else "Alcoholic"
    if "non-alcoholic" in name or "alcoholic" in name:
      drink_name = "%20".join(name[:len(name)-2])
    else:
      drink_name = "%20".join(name)
    await ctx.send("You asked for a " + " ".join(drink_name))
    # get drink by name
    r = requests.get("https://www.thecocktaildb.com/api/json/v1/1/search.php?s=%s&a=%s" % (drink_name, alcoholic)).json()
    drink_info = await self.get_drink_info(r['drinks'])
    async with ctx.typing():
      await ctx.send(drink_info[0])
      await asyncio.sleep(random.randrange(4, 6))
      return await ctx.send(drink_info[1])
    
  @commands.command(aliases=['ingredient_drink'])
  async def i_drink(self, ctx, ingredient):
    if not self.happy_hour:
      return await ctx.send("Sorry, friend. Come back at 5pm when we're open.  Feel free to take some complimentary `!coffee`.")
    await self.add_stat(ctx.author.id)
    r = requests.get("https://www.thecocktaildb.com/api/json/v1/1/filter.php?i=" + ingredient)
    drink_info = await self.get_drink_info(r['drinks'])
    await ctx.send("You got it, boss. Let me see what I can make with that.")
    async with ctx.typing():
      await ctx.send(drink_info[0])
      await asyncio.sleep(random.randrange(4, 6))
      return await ctx.send(drink_info[1])
  
  @commands.command(aliases=['random_drink', 'rdrink', 'rand_drink', 'randdrink'])
  async def r_drink(self, ctx):
    if not self.happy_hour:
      return await ctx.send("Sorry, friend. Come back at 5pm when we're open. Feel free to take some complimentary `!coffee`.")
    await self.add_stat(ctx.author.id)
    # get random drink
    r = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php").json()
    drink_info = await self.get_drink_info(r['drinks'])
    async with ctx.typing():
      await ctx.send(drink_info[0])
      await asyncio.sleep(random.randrange(4, 6))
      return await ctx.send(drink_info[1])
  
  @commands.command()
  async def bardown(self, ctx):
    tz_ = tz.timezone("EST")
    cur_time = datetime.now(tz=tz_)
    fivepm = datetime(cur_time.year, cur_time.month, cur_time.day, 16, 0, 0, tzinfo=tz_)
    countdown = (fivepm - cur_time)
    count_hours, count_minutes = countdown.seconds//3600, (countdown.seconds//60)%60
    count_seconds = countdown.seconds - count_hours*3600 - count_minutes*60
    # build and send string
    ret_string = str(count_hours) + " hours, " + str(count_minutes) + " minutes and " + str(count_seconds) + " seconds until Obotma's Shabby but Classy Cabaret opens. Have come complimentary `!coffee` in the meantime.\nFree drinks for our first week's grand opening!"
    return await ctx.send(ret_string)

  @commands.command()
  async def coffee(self, ctx):
    r = requests.get("https://coffee.alexflipnote.dev/random.json").json()
    if r and 'file' in r:
      return await ctx.send(r['file'])
    else:
      return await ctx.send("Looks like we're all out of coffee. Sorry, boss.")
  
  async def get_drink_info(self, drinks):
    if drinks:
      drink = random.choice(drinks)
      # get ingredients
      ingredients = []
      ingredient_num = 1
      ingredient_name = "strIngredient" + str(ingredient_num)
      while drink[ingredient_name]:
        ingredients.append(drink[ingredient_name])
        ingredient_num += 1
        ingredient_name = "strIngredient" + str(ingredient_num)
      info_string = "You got it, boss. Let me whip that up for you.\n" + "**" + drink['strDrink'] + "** *(" + drink['strCategory'] + ")*, " + drink['strAlcoholic'] + "\n**Glass**: *" + drink['strGlass'] + "*\n" + "**Ingredients: **" + ", ".join(ingredients) + "\n**Instructions**: " + drink['strInstructions'] + "\n Here you are. Enjoy!"
      image_url = drink['strDrinkThumb'] if drink['strDrinkThumb'] else ''
      return (info_string, image_url)
    else:
      return ("None of that behind the bar, boss. Can I get you something else?", "https://tenor.com/view/i-must-be-of-service-chris-conner-poe-altered-carbon-i-must-provide-service-gif-17622348")
  
  @commands.command()
  async def open_bar(self, ctx):
    if ctx.author.id == gl.my_user_id:
      self.happy_hour = True
      return await ctx.send("Bar's open, everybody!")
    else:
      return await ctx.send("https://tenor.com/view/let-me-in-eric-andre-wanna-come-in-gif-13730108")
  
  @commands.command()
  async def close_bar(self, ctx):
    if ctx.author.id == gl.my_user_id:
      self.happy_hour = False
      await ctx.send("Bar's closing, last call for drinks.")
      await asyncio.sleep(60)
      return await ctx.send("Drive drunk, chads")
    else:
      await ctx.send("https://tenor.com/view/fun-sucker-party-pooper-thief-of-joy-you-are-a-thief-of-joy-the-office-gif-11156413")
      return await ctx.send("Keep on drinking, lads")
  
  @tasks.loop(hours=24)
  async def bar_open(self):
    channel = gl.bot.get_channel(604834176645988354) # chats and bants
    # channel = gl.bot.get_channel(887682725375528963) # testing chat    
    self.happy_hour = True
    await channel.send("Bar is open, gents. Come order your drinks and stay a while.")

  @bar_open.before_loop
  async def before_bar_open(self):
    await gl.bot.wait_until_ready()
    tz_ = tz.timezone("EST")
    cur_time = datetime.now(tz=tz_)
    fivepm = datetime(cur_time.year, cur_time.month, cur_time.day, 16, 0, 0, tzinfo=tz_)
    tdelta = (fivepm - cur_time)
    await asyncio.sleep(tdelta.seconds)
  
  @tasks.loop(hours=24)
  async def bar_close(self):
    channel = gl.bot.get_channel(604834176645988354) # chats and bants
    # channel = gl.bot.get_channel(887682725375528963) # testing chat
    await channel.send("Bar's closed, everyone. You don't have to go home, but you can't stay here. Have a good night.")
    self.happy_hour = False
  
  @bar_close.before_loop
  async def before_bar_close(self):
    await gl.bot.wait_until_ready()
    tz_ = tz.timezone("EST")
    cur_time = datetime.now(tz=tz_)
    # sleep until 'bar closes' at 4am next day
    bar_closes = datetime(cur_time.year, cur_time.month, cur_time.day+1, 3, 0, 0, tzinfo=tz_)
    tdelta = (bar_closes - cur_time)
    await asyncio.sleep(tdelta.seconds)
  
  async def add_stat(self, id):
    id = str(id)
    if id not in db['drink_stats']:
      db['drink_stats'][id] = 1
    else:
      db['drink_stats'][id] += 1