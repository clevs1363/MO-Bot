import random
from discord.ext import commands

class Dice(commands.Cog):
  # commands associated with the built-in dice roller
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command(aliases=['r'])
  async def roll(self, ctx, roll):
    if roll == "stats":
      stats = await self.roll_stats()
      await ctx.send(", ".join([str(stat) for stat in stats]))
      total = sum(stats)
      if total > 75:
        await ctx.send("Damn. I like ya stats, g")
      elif total < 75 and total > 69:
        await ctx.send("*light applause*")
      else:
        await ctx.send("https://i.ibb.co/KWK4Ysk/badroll.jpg")
      return
    try:
      if roll.startswith("d"):
        # interpet as one dice
        num = 1
        dice = roll[1:]
      else:
        data = roll.split("d")
        num = int(data[0])
        dice = data[1]
      mods_raw = dice.split("+")
      if len(mods_raw) == 1:
        # no modifiers
        mods = 0
      else:
        mods = int(mods_raw[1])
      dice = int(mods_raw[0]) # dice will always be first element
      result = ""
      total = 0
      for res in range(num):
        rolled = random.randrange(1, dice+1)
        total += rolled
        result += str(rolled) + ", "
      total += mods
      if total - mods == 20 and num == 1 and dice == 20: # only trigger on nat 1d20
        await ctx.send('https://ih1.redbubble.net/image.756099120.1069/st,small,507x507-pad,600x600,f8f8f8.u2.jpg')
      elif total - mods == 1 and num == 1 and dice == 20:
        await ctx.send('https://ih1.redbubble.net/image.1047087046.0562/st,small,845x845-pad,1000x1000,f8f8f8.u1.jpg')
      else:
        await ctx.send(result[:-2]) # sliced to remove last ', '
      if mods != 0:
        await ctx.send("Total = " + str(total))
    except Exception as e:
      print(e)
      await ctx.send("Error: dice fell off the table. Reformat and try again")
  
  async def roll_stats(self):
    stats = []
    for roll in range(6):
      drop_lowest = [random.randrange(1, 7) for x in range(4)]
      drop_lowest.remove(min(drop_lowest))
      stats.append(sum(drop_lowest))
    return stats