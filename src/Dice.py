import random
import requests
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

  @commands.command()
  async def statblock(self, ctx, type, *name):
    # type is spell, monster, etc; name is name
    # metadata: name, type, size, etc. top 3rd of the sheet
    # stats: actual stat numbers
    # charcts: (characteristics) resistances, immunities, etc. middle 3rd
    name = "-".join(name)
    url = "https://www.dnd5eapi.co/api/"+type+"/"+name+"/"
    print(url)
    r = requests.get(url).json()
    print(r)
    if "error" in r:
      await ctx.send("Something went wrong:")
      return await ctx.send("*"+r["error"]+"*")
    if type == "spells":
      return
    elif type == "monsters":
      metadata = f"{r['name']} \n{r['size']} {r['type']}, {r['alignment']}\n"
      metadata += "---------------------------\n"
      metadata += f"**AC** {r['armor_class']}\n**Hit Points** {r['hit_points']} ({r['hit_dice']}\n"
      for type, num in r['speed'].items():
        metadata += type + ": " + num
      metadata += "---------------------------\n"
    stats = f"[{r['strength']}] | [{r['dexterity']}] | [{r['constitution']}] | [{r['wisdom']}] | [{r['intelligence']}] | [{r['charisma']}]"
    stats += "---------------------------\n"
    saves = "**Saving Throws** "
    skills = "**Skills** "
    for p in r["proficiencies"]:
      if "saving-throw" in p["proficiency"]["index"]:
        saves += p["proficiency"]["name"].split(" ")[-1] + " +" + str(p["value"]) + ", "
      elif "skill" in p["proficiency"]["index"]:
        skills += p["proficiency"]["name"].split(" ")[-1] + " +" + str(p["value"]) + ", "
    charcts = saves[:-1] + "\n" + skills[:-2] # remove final ", "
    for charct in ["damage_vulnerabilities", "damage_resistances", "damage_immunities", "condition_immunities"]:
      if r[charct]: 
        charct_text = charct.replace("_", "").capitalize()
        charct_results = ", ".join(r[charct])
        charcts += "**" + charct_text + "** " + charct_results + "\n"
    for type, num in r["senses"].items():
      charcts += type + ": " + num
    charcts += f"**Languages** {r['languages']}\n**Challenge** {r['challenge_rating']} ({r['xp']})\n"
    charcts += "---------------------------\n"
    abilities = ""
    for sa in r["special_abilities"]:
      if "usage" in sa:
        abilities += f"***{sa['name']}** {sa['usage']['times']}/{sa['usage']['type']}. {sa['desc']}\n"
      else:
        abilities += f"**{sa['name']}** {sa['desc']}\n"
    actions = "__***ACTIONS.***__---------------------------\n"
    for a in r["actions"]:
      actions += f"***{a['name']}***. {a['desc']}"
    bactions = "__***BONUS ACTIONS.***__---------------------------\n"
    for b in r["bonus_actions"]:
      bactions += f"***{b['name']}***. {b['desc']}"
    lactions = "__***LEGENDARY ACTIONS.***__---------------------------\n"
    for l in r["legendary_actions"]:
      lactions += f"***{l['name']}***. {l['desc']}"
    await ctx.send(metadata)
    await ctx.send(stats)
    await ctx.send(charcts)
    await ctx.send(abilities)
    await ctx.send(actions)
    await ctx.send(bactions)
    await ctx.send(lactions)
    return