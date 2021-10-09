from discord.ext import commands
import globals as gl
import discord

class Emotes(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

  @commands.command()
  async def ue(self, ctx, emote_name):
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

  
  @commands.command()
  async def e(self, ctx, *emote_name):
    if not emote_name:
      await ctx.send("Please provide the emote name: !e <name>")
      return
    emote_name = emote_name[0]
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
        for emoji in ctx.guild.emojis:
          if emoji.name == emote_name:
            await msg.add_reaction(emoji)
        await ctx.message.delete() # delete triggering message
    else:
      # send emoji in chat
      for emoji in ctx.guild.emojis:
        if emoji.name == emote_name:
          await ctx.send(str(emoji))
          await ctx.message.delete() # delete triggering message
          return
      # if not returned by now, emote doesn't exists
      await ctx.send("Emote doesn't exist, try again")
  
  