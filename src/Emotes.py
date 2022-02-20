from discord.ext import commands
import globals as gl
import discord
import re

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
  
  @commands.command()
  async def big(self, ctx, name):
    await ctx.invoke(gl.bot.get_command('smoosh'), emoji1=name, emoji2=name)
    return await ctx.message.delete()
  
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