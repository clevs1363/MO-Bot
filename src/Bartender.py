from discord.ext import commands
import requests
import random
import asyncio

class Bartender(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    # set timer to say something at 5:00pm
  
  @commands.command()
  async def drink(self, ctx, name, alcoholic=""):
    if alcoholic:
      alcoholic = "Alcoholic" if alcoholic in ("yes", "a", "alcoholic") else "Non_Alcoholic"
    # get drink by name
    r = requests.get("https://www.thecocktaildb.com/api/json/v1/1/search.php?s=%s&a=%s" % (name, alcoholic)).json()
    drink_info = await self.get_drink_info(r['drinks'])
    await ctx.send("You got it, boss. Let me whip that up for you.")
    async with ctx.typing():
      await ctx.send(drink_info[0])
      await asyncio.sleep(random.randrange(4, 6))
      await ctx.send("Here you are. Enjoy!")
      return await ctx.send(drink_info[1])
  
  @commands.command(aliases=['random_drink', 'rdrink', 'rand_drink', 'randdrink'])
  async def r_drink(self, ctx):
    # get random drink
    r = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php").json()
    drink_info = await self.get_drink_info(r['drinks'])
    await ctx.send("You got it, boss. Let me whip that up for you.")
    async with ctx.typing():
      await ctx.send(drink_info[0])
      await asyncio.sleep(random.randrange(4, 6))
      await ctx.send("Here you are. Enjoy!")
      return await ctx.send(drink_info[1])
  
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
      info_string = "**" + drink['strDrink'] + "** *(" + drink['strCategory'] + ")*, " + drink['strAlcoholic'] + "\n**Glass**: *" + drink['strGlass'] + "*\n" + "**Ingredients: **" + ", ".join(ingredients) + "\n**Instructions**: " + drink['strInstructions']
      image_url = drink['strDrinkThumb'] if drink['strDrinkThumb'] else ''
      return (info_string, image_url)
    else:
      return ("None of that behind the bar, boss. Can I get you something else?", "https://tenor.com/view/i-must-be-of-service-chris-conner-poe-altered-carbon-i-must-provide-service-gif-17622348")
  
  """
  TODO:
  -"Tab" system
  -More responses
  -Basic drinks (beer, whiskey, etc.)
  """