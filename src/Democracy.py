from discord.ext import commands
import globals as gl
import asyncio
import math
import time
import random

"""
Democratic functions:
- Add/remove an emote
- Add/remove a channel
- Set the channel topic
- Add/remove a role
- Assign role
- Put Obotma to sleep
"""

class Democracy(commands.Cog):
  # commands associated with making the server a Democracy
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.votes = {}
    self.num_votes_needed = math.ceil(0.75 * len([member for member in ctx.guild.members if not member.bot]))

  @commands.command()
  async def remove_emote(self, ctx, name):
    em_to_rem = None # emoji to remove
    for e in ctx.guild.emojis:
      if e.name == name:
        em_to_rem = e
    if not em_to_rem:
      return await ctx.send("Emoji " + name + " not found.")
    vote_text = "Remove emote " + str(em_to_rem)
    code = await self.vote(ctx, vote_text)
    if code == 0:
      await ctx.send("Removing " + str(em_to_rem) + ". Say your last goodbyes. Execution in 10...")
      for i in range(9, 1, -1):
        await ctx.send(str(i) + "...")
        time.sleep(1)
      # delete emote
    elif code == 1:
      await ctx.send(str(em_to_rem) + " lives to see another day.")
      await ctx.invoke(self.bot.get_command('re'))
    else:
      return await ctx.send("A code was returned from the vote that shouldn't have been.")

  @commands.command()
  async def add_channel(self, ctx, name):
    vote_text = "Add channel " + name
    code = await self.vote(ctx, vote_text)
    if code == 0:
      await ctx.send("Adding the channel " + name + ".")
      # add channel
    elif code == 1:
      await ctx.send(name + " remains in beauracratic purgatory.")
      return await ctx.invoke(self.bot.get_command('re'))
    else:
      return await ctx.send("A code was returned from the vote that shouldn't have been.")

  @commands.command()
  async def set_topic(self, ctx, *topic):
    topic = " ".join(topic)
    vote_text = "Set the channel topic to " + topic
    code = await self.vote(ctx, vote_text)
    if code == 0:
      await ctx.send("Okay then. Time to stay on topic.")
      # set topic
    elif code == 1:
      await ctx.send("Looks like we're going to be staying off topic.")
      return await ctx.invoke(self.bot.get_command('re'))
    else:
      return await ctx.send("A code was returned from the vote that shouldn't have been.")
    return

  @commands.command()
  async def add_role(self, ctx, name):
    return

  @commands.command()
  async def assign_role(self, ctx, role_name, *users):
    return

  @commands.command()
  async def sleep(self, ctx):
    nap_time = random.choices([5, 15, 30, 60, 90, 480], weights=(40, 30, 15, 10, 4, 1), k=1)[0]
    vote_text = "Put me to sleep for" + str(nap_time) + " minutes?"
    code = await self.vote(ctx, vote_text)
    if code == 0:
      await ctx.send("https://tenor.com/view/golden-retriever-sleep-yawn-dog-puppy-gif-16433231")
      # sleep program
      # time.sleep(nap_time*60)
    elif code == 1:
      await ctx.send("I was hardly even sleepy!")
      return await ctx.send("https://tenor.com/view/hyper-gif-18023825")
    else:
      return await ctx.send("A code was returned from the vote that shouldn't have been.")
    return

  async def vote(self, ctx, vote_text):
    """Return codes:
    0 - vote yes
    1 - vote no
    """
    await ctx.send("[[VOTE]] " + vote_text + "? 60 second counter begins now.")
    def check(reaction, user):
      return user == ctx.message.author and str(reaction.emoji) in ['👍', '👎'] and reaction.count == self.num_votes_needed
      
    try:
      reaction, user = await gl.bot.wait_for('reaction_add', timeout=60.0, check=check)
      if reaction.emoji == '👍':
        return 0
      elif reaction.emoji == '👎':
        return 1
      return
    except asyncio.TimeoutError:
      return await ctx.send("Vote timed out. No changes will be made.")
    else:
      return await ctx.send("I have no idea what happens here. I think an error happened or something")
    return -1
    