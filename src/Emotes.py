from discord.ext import commands
import globals as gl
import discord
import re
import random
from PIL import Image
from io import BytesIO
from collections import defaultdict

class Emotes(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command(aliases=['ue'])
  async def upload_emote(self, ctx, emote_name):
    # stand for upload emoji
    if ctx.message.author.id == gl.my_user_id:
      with open(r"docs/assets/" + emote_name, "rb") as img:
        img_byte = img.read()
        emoji_exists = False
        for emoji in ctx.guild.emojis:
          if emoji.name == emote_name:
            emoji_exists = True
        if not emoji_exists:
          await ctx.message.delete() # delete triggering message
          emote_name = emote_name[:-4] # strip filename
          new_emoji = await ctx.message.guild.create_custom_emoji(name = (emote_name), image = img_byte)
          await ctx.send(str(new_emoji) + " has been uploaded!")
        else:
          await ctx.send("Emoji already exists")
    else:
      await ctx.send(gl.nope)

  
  @commands.command(aliases=['e'])
  async def emote(self, ctx, emote_name, num=1):
    if not emote_name:
      await ctx.send("Please provide the emote name: !e <name>")
      return
    # emote_name = emote_name[0]
    emote_name = re.sub("[0-9]{18}", "", emote_name).replace(":", "").replace("<", "").replace(">", "")
    if emote_name in ('wetawd', 'advanced'):
      emote_name = 'fwend'
    elif emote_name == 'schizo':
      return await ctx.send("Emote exists, don't you remember?")
    elif emote_name == 'edited':
      await ctx.send("Certified Drew moment.")
    elif emote_name == 'fred':
      for emoji in ctx.guild.emojis:
        if emoji.name == 'pepestress':
          await ctx.send(str(emoji) + 'fred spooks me, sorry friend')
          return
    elif emote_name == 'fwend':
      await ctx.send('You\'re a good friend too, ' + ctx.author.display_name + '.')
    if ctx.message.reference:
      # react to message reply
      msg = ctx.message.reference.resolved # the reply itself
      if emote_name == "pride" and random.randrange(1, 100) == 1:
        return await msg.add_reaction("🏳️‍🌈")
      if type(msg) == discord.Message: # only trigger if Message not DeletedReferencedMessage
        for guild in gl.bot.guilds:
          for emoji in guild.emojis:
            if emoji.name == emote_name:
              await msg.add_reaction(emoji)
          await ctx.message.delete() # delete triggering message
    else:
      # send emoji in chat
      for guild in gl.bot.guilds:
        for emoji in guild.emojis:
          if emoji.name == emote_name:
            if len(str(emoji)) * num > 2000:
              return await ctx.send("The message would be too long, Drew.")
            if emoji.name == "pride" and random.randrange(1, 100) == 1:
              emoji = "🏳️‍🌈"
            emoji_string = ""
            for x in range(num):
              emoji_string += str(emoji)
            await ctx.send(emoji_string)
            await ctx.message.delete() # delete triggering message
            return 
      # if not returned by now, emote doesn't exists
      await ctx.send("Emote doesn't exist, try again")
  
  @commands.command(aliases=['edit'])
  async def edited(self, ctx):
    edited = await gl.get_emoji(ctx.guild, "edited")
    s = """:edited::edited::edited:     :edited::edited:        :edited::edited::edited::edited:     :edited::edited::edited::edited:
:edited:                 :edited:   :edited:              :edited:                        :edited:
:edited::edited: :edited:    :edited:     :edited:            :edited:                        :edited:
:edited:                 :edited:   :edited:              :edited:                        :edited:
:edited::edited: :edited:    :edited::edited:        :edited::edited::edited::edited:              :edited:"""
    edited_str = s.replace(":edited:", str(edited))
    return await ctx.send(edited_str)
  
  @commands.command(aliases=['rb'])
  async def big(self, ctx, *n):
    rand_len = 0
    for guild in gl.bot.guilds:
      rand_len += len(guild.emojis)
    img_bytes = []
    if not n:
      rand_num = random.randrange(1, rand_len)
      counter = 1
      for guild in gl.bot.guilds:
        for emoji in guild.emojis:
          if counter == rand_num:
            i = await emoji.url.read()
            img_bytes.append(i)
          counter += 1
    else:
      name = n[0]
      for guild in gl.bot.guilds:
        for emoji in guild.emojis:
          if emoji.name == name:
            i = await emoji.url.read()
            img_bytes.append(i)
    if img_bytes:
      img = Image.open(BytesIO(random.choice(img_bytes)), mode='r')
      b = BytesIO()
      img.save(b, "PNG")
      b.seek(0)
      return await ctx.send(file=discord.File(b, filename='big.png'))
    else:
      return await ctx.send("Emoji not found :(")
      
  
  @commands.command(aliases=['1984'])
  async def _1984(self, ctx):
    msg = ctx.message.reference
    if msg: 
      msg = msg.resolved
      await msg.add_reaction("1️⃣")
      await msg.add_reaction("9️⃣")
      await msg.add_reaction("8️⃣")
      await msg.add_reaction("4️⃣")
      return await ctx.message.delete()
    else:
      return await ctx.channel.send("1️⃣ 9️⃣ 8️⃣ 4️⃣")

  @commands.command()
  async def based(self, ctx):
    msg = ctx.message.reference
    if msg: 
      msg = msg.resolved
      await msg.add_reaction("🇧")
      await msg.add_reaction("🇦")
      await msg.add_reaction("🇸")
      await msg.add_reaction("🇪")
      await msg.add_reaction("🇩")
      return await ctx.message.delete()
    else:
      return await ctx.channel.send("🇧 🇦 🇸 🇪 🇩")

  @commands.command()
  async def cringe(self, ctx):
    msg = ctx.message.reference
    if msg: 
      msg = msg.resolved
      await msg.add_reaction("🇨")
      await msg.add_reaction("🇷")
      await msg.add_reaction("🇮")
      await msg.add_reaction("🇳")
      await msg.add_reaction("🇬")
      await msg.add_reaction("🇪")
      return await ctx.message.delete()
    else:
      return await ctx.channel.send("🇨 🇷 🇮 🇳 🇬 🇪")

  @commands.command(aliases=['re'])
  async def random_emote(self, ctx, num=1):
    rand_len = 0
    for guild in gl.bot.guilds:
      rand_len += len(guild.emojis)
    rand_num = random.randrange(1, rand_len)
    counter = 1
    if ctx.message.reference:
      # react to message reply
      msg = ctx.message.reference.resolved # the reply itself
      if type(msg) == discord.Message: # only trigger if Message not DeletedReferencedMessage
        for guild in gl.bot.guilds:
          for emoji in guild.emojis:
            if rand_num == counter:
              await msg.add_reaction(emoji)
            counter += 1
        return await ctx.message.delete() # delete triggering message
    else:
      # send emoji in chat
      for guild in gl.bot.guilds:
        for emoji in guild.emojis:
          if rand_num == counter:
            if len(str(emoji)) * num > 2000:
              return await ctx.send("The message would be too long, Drew.")
            emoji_string = ""
            for x in range(num):
              emoji_string += str(emoji)
            await ctx.send(emoji_string)
            return await ctx.message.delete() # delete triggering message
          counter += 1
      # if not returned by now, weird error happened
      return await ctx.send("Something went wrong, please try again")

  @commands.command(aliases=['em_rec'])
  async def emojis_received(self, ctx, emote_name, history):
    if not ctx.message.author.id == gl.my_user_id:
      return await ctx.send("no")
    # counts and sorts number of emote_names received
    emojis_received = defaultdict(int)
    messages = defaultdict(int)
    async with ctx.typing():
      for channel in ctx.guild.text_channels:
        if int(channel.id) == 783773695231393803 or int(channel.id) == 940300465399291904:
          continue # ignore the hidden chats
        async for msg in channel.history(limit=int(history)):
          messages[msg.author.name] += 1
          for react in msg.reactions:
            filtered_emote_name = re.sub("[0-9]{18}", "", str(react)).replace(":", "").replace("<", "").replace(">", "") # filters out internal emoji representation
            if filtered_emote_name == emote_name:
              emojis_received[msg.author.name] += 1
    if emojis_received:
      sorted_emojis = {k: v for k, v in sorted(emojis_received.items(), key=lambda item: item[1], reverse=True)}
      ratios = {}
      # put raw number of emojis received in a string
      count_string = "Raw number of emojis received:\n"
      count = 1
      biglaff_emote = await gl.get_emoji(ctx.guild, emote_name)
      for k, v in sorted_emojis.items():
        count_string += str(count) + ". " + k + ": " + str(v)
        if biglaff_emote:
          count_string += " " + str(biglaff_emote) + "s\n"
        else:
          count_string += " " + emote_name + "s\n"
        count += 1
      # get ratio of messages sent to emojis received
      for (user, num) in messages.items():
        if user in emojis_received: # checks if exist
          ratios[user] = round(num / emojis_received[user], 2)
      sorted_ratios = {k: v for k, v in sorted(ratios.items(), key=lambda item: item[1])}
      # put ratio in string
      ratio_string = "Ratio of messages sent to emojis received (lower number is \"better\"), indicating the average number of messages sent before receiving one of the emojis:\n"
      count = 1
      for (k, v) in sorted_ratios.items():
        ratio_string += str(count) + ". " + k + ": " + str(v)
        if biglaff_emote:
          ratio_string += " messages per " + str(biglaff_emote) + "\n"
        else:
          ratio_string += " messages per " + emote_name + "\n"
        count += 1
      # send final strings
      await ctx.send(count_string)
      return await ctx.send(ratio_string)
    else:
      return await ctx.send("No emojis with that name were found.")

  @commands.command()
  async def salt_counter(self, ctx):
    if not ctx.message.author.id == gl.my_user_id:
      return await ctx.send("no")
    # counts and sorts number of emote_names received
    messages_edited = defaultdict(int)
    ambulances_rec = defaultdict(int)
    async with ctx.typing():
      for channel in ctx.guild.text_channels:
        async for msg in channel.history(limit=100000):
          if msg.edited_at:
            messages_edited[msg.author.name] += 1
          for reaction in msg.reactions:
            # print(str(reaction))
            if str(reaction) == "🚑":
              ambulances_rec[msg.author.name] += 1
    sorted_edited = dict(sorted(messages_edited.items(), key=lambda item: item[1], reverse=True))
    sorted_ambulances = dict(sorted(ambulances_rec.items(), key=lambda item: item[1], reverse=True))
    edited_string = await self.print_dict("Messages edited:\n", sorted_edited)
    ambulance_string = await self.print_dict("Ambulances received:\n", sorted_ambulances)
    await ctx.send(edited_string)
    return await ctx.send(ambulance_string)

  async def print_dict(self, initial_str, dict):
    ret_string = initial_str
    counter = 1
    for (k, v) in dict.items():
      ret_string += str(counter) + ". " + k + ": " + str(v) + "\n"
      counter += 1
    return ret_string
            