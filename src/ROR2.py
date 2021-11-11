from discord.ext import commands
from datetime import datetime
from pytz import timezone
from replit import db
import re
import discord
import asyncio
import random
import globals as gl

class ROR2(commands.Cog):
  # commands associated with ror2 and swaggin
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.swag_id = 0
    self.swaggers = []
    self.characters = ['Acrid', 'Artificer', 'Bandit', 'Captain', 'Commando', 'Engineer', 'Huntress', 'Loader', 'Mercenary', 'MUL-T', 'REX'] 
    self.artifacts = {
      'Chaos': 'Friendly fire is enabled for both survivors and monsters alike.', 
      'Command': 'Choose your items.', 
      'Death': 'When one player dies, everyone dies. Enable only if you want to truly put your teamwork and individual skill to the ultimate test.', 
      'Dissonance': 'Monsters can appear outside their usual environments.',
      'Enigma': 'Spawn with a random equipment that changes every time it\'s activated.',
      'Evolution': 'Monsters gain items between stages.',
      'Frailty': 'Fall damage is doubled and lethal.',
      'Glass': 'Allies deal 500% damage, but have 10% health.',
      'Honor': 'Enemies can only spawn as elites.',
      'Kin': 'Monsters will be of only one type per stage.',
      'Metamorphosis': 'Players always spawn as a random survivor.',
      'Sacrifice': 'Monsters drop items on death, but Chests no longer spawn.',
      'Soul': 'Wisps emerge from defeated monsters.',
      'Spite': 'Enemies drop multiple exploding bombs on death.',
      'Swarms': 'Monster spawns are doubled, but monster maximum health is halved.',
      'Vengeance': 'Your relentless doppelganger will invade every 10 minutes.'
    }
    # del db['swag_report'] # need to remove testing stats
    if 'swag_report' not in db.keys():
      db['swag_report'] = {
        "win": 0,
        "loss": 0
      }
  
  @commands.command(aliases=['shag'])
  async def swag(self, ctx, *swag_time):
    if not swag_time:
      return await ctx.send("Provide a time (!swag <time>)")
    else:
      # verify time formatting
      t = str(swag_time[0])
      if len(t) == 5:
        # military time. Example: 17:50
        time_regex = re.compile("^([0-2][0-4]):([0-5][0-9])$")
        is_standard_time = False # needed check to add 12 hours or not
      else:
        # standard time. Example: 11:00am
        time_regex = re.compile("^(([0-1][1-2])|([1-9])):[0-5][0-9](pm|am)$")
        is_standard_time = True # needed check to add 12 hours or not
      if not time_regex.match(t):
        await ctx.send("Please put a correct time format. Either HH:MM for military time, or HH:MMxm for standard time.")
        return

      # parse verified time
      time_data = t.split(":")
      hour = int(time_data[0])
      if is_standard_time:
        # hours are shifted an hour off because of the nature of tz EST timezone
        hour += 12
      # split until index 2 in case it's of the form MMxm
      # Example: 
      # 12:00pm -> time_data = ['12', '00pm']
      #            time_data[1][:2] = '00'
      minute = int(time_data[1][:2]) # subtract 10 for target notification
      if minute < 10:
        minute += 50 # accounts for time rounding
      else:
        minute -= 10
      print(hour, minute)
      # put bot to sleep until 10 minutes before swag to @ everyone
      tz = timezone('EST')
      now = datetime.now(tz) 
      future = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)
      
      # send swag embed
      self.swaggers = []
      embed = discord.Embed(
        title = "Swag at " + str(t) +"?",
        description = "React yes, no, or maybe below",
        color = discord.Color.dark_blue()
      )
      embed.set_author(name="Risk of Rain 2", icon_url= "https://www.gamespot.com/a/uploads/original/1575/15759911/3719483-risk-of-rain-2-review-promothumb.jpg")
      embed.add_field(name = "Yes:", value = "\N{thumbs up sign}")
      embed.add_field(name = "No:", value = "\N{thumbs down sign}")
      embed.add_field(name = "Maybe:", value = "\N{shrug}")

      # get ror2 role id
      role_id = await gl.get_role(ctx, "ror2")
      await ctx.send("<@&" + str(role_id) + ">")
      msg = await ctx.send(embed=embed)
      await msg.add_reaction("\N{thumbs up sign}")
      await msg.add_reaction("\N{thumbs down sign}")
      await msg.add_reaction("\N{shrug}")
      self.swag_id = msg.id
      
      await asyncio.sleep((future-now).seconds) # sleep until 10 minutes before swag

      # notify swaggers
      tag_string = " ".join(["<@"+str(swagger[1])+">" for swagger in self.swaggers]) + ": swag in 10 minutes"
      if tag_string:
        await ctx.send(tag_string)
      else:
        await ctx.send("No one will be swagging :(")
      return
  
  @commands.command()
  async def swaggers(self, ctx):
    if self.swaggers:
      await ctx.send("Current swaggers: ")
      await ctx.send(" ".join([swagger[0] for swagger in self.swaggers]))
    else:
      await ctx.send("No swaggers yet. Use !swag to initiate a potential swag. Will remove previous swagger session")
      await ctx.send("https://i.ibb.co/f1fwZRf/john-travolta-lost-ror2.gif")
  
  @commands.command(aliases=['rand_swag', 'r_swag'])
  async def random_swag(self, ctx, num=0):
    for swagger in self.swaggers:
      await ctx.send(swagger + ": " + random.choice(self.characters))
    if num:
      num = int(num)
      if num <= 16 and num >= 0:
        chosen_artifacts = []
        for artifact in range(num):
          # ensure every addition is unique
          unique = False
          while not unique:
            rand_artifact = random.choice(list(self.artifacts.keys()))
            if rand_artifact in chosen_artifacts:
              unique = False
            else:
              chosen_artifacts.append(rand_artifact)
              unique = True
        await ctx.send("Artifacts: " + ", ".join(chosen_artifacts))
      else:
        await ctx.send("Enter a valid number of artifacts between 0 and 16")
        await ctx.send("https://i.ibb.co/f1fwZRf/john-travolta-lost-ror2.gif")
    else:
      await ctx.send("No artifacts selected.")
  
  @commands.command()
  async def artifact(self, ctx, artifact):
    if artifact in self.artifacts:
      await ctx.send(self.artifacts[artifact])
    else:
      await ctx.send("Artifact not found")
      await ctx.send("https://i.ibb.co/f1fwZRf/john-travolta-lost-ror2.gif")

  @commands.command()
  async def swag_report(self, ctx, *result):
    if result:
      result = result[0]
      print(result)
      if result != 'win' and result != 'loss':
        await ctx.send("Please use [win] or [loss]")
        return
      if self.swaggers:
        # add result to storage and clear ses
        db['swag_report'][result] += 1
        self.swaggers = []
      else:
        return await ctx.send("No swag ses to report on.")
    # no need for an else statement, this will run regardless
    await ctx.send("--CURRENT STATS-- \n<:yes:743651437585891407> **The Boys**: " + str(db['swag_report']['win']) + "\n<:autism:743828537601163294> **Mithrix**: " + str(db['swag_report']['loss']))
  
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    if not user.name == gl.bot.user and reaction.message.id == self.swag_id and reaction.emoji == "\N{thumbs up sign}":
      if reaction.count > 5:
        await reaction.message.channel.send("Already at 4 swaggers :(")
        await reaction.remove(user)
      else:
        await reaction.message.channel.send(user.name + " will be swagging.")
        self.swaggers.append((user.name, user.id))
  
  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction, user):
    if reaction.emoji == "\N{thumbs up sign}":
      await reaction.message.channel.send(user.name + " will no longer be swagging.")
      self.swaggers.remove((user.name, user.id))