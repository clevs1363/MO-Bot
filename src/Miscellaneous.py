from discord.ext import commands
from datetime import date
import globals as gl
import discord
from replit import db

class Miscellaneous(commands.Cog):
  # Miscellaneous commands
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.inktober_prompts = ['Crystal', 'Suit', 'Vessel', 'Knot', 'Raven', 'Spirit', 'Fan', 'Watch', 'Pressure', 'Pick', 'Sour', 'Stuck', 'Roof', 'Tick', 'Helmet', 'Compass', 'Collide', 'Moon', 'Loop', 'Sprout', 'Fuzzy', 'Open', 'Leak', 'Extinct', 'Splat', 'Connect', 'Spark', 'Crispy', 'Patch', 'Slither', 'Risk']

  @commands.command(aliases=['h'])
  async def help(self, ctx):
    embed = discord.Embed(
    title = "Obotma Commands",
    description = "A fun passion project for the boys. It started as a replacement to Groovy and Rhythm, and has evolved into a collection of random commands for the server. \n\n https://clevs1363.github.io/Obotma/",
    color = discord.Color.dark_blue()
    )
    embed.set_author(name=gl.bot.user.name, icon_url=gl.bot.user.avatar_url)
    await ctx.send(embed=embed)

  @commands.command()
  async def die(self, ctx):
    async with ctx.typing():
      return await ctx.send("I'd rather die standing than live kneeling \n And I don't even have legs")
  
  @commands.command()
  async def kill(self, ctx):
    return await ctx.send('https://tenor.com/view/braun-strow-man-you-cant-kill-me-gif-10197798')

  @commands.command()
  async def ses(self, ctx, *msg):
    async with ctx.typing():
      await gl.add_emoji(ctx.message, 'ses', gl.bot.emojis)
      if msg: # check if arguments were passed
        if ctx.author.id == gl.my_user_id:
          output = " ".join(msg)
          await ctx.message.channel.edit(topic = output)
          await gl.update_ses('ses', output)
          await ctx.send('--SESSION CHANGED--')
        else:
          return await ctx.send(gl.no_gif)
      return await ctx.send(db['ses'])

  @commands.command()
  async def abyses(self, ctx, *msg):
    await gl.add_emoji(ctx.message, 'ses', gl.bot.emojis)
    if msg: # check if arguments passed
      if ctx.author.name == "Ś̶̨h̸̥͌r̷̬̍ö̷͉o̴̡͐m̶̧̏b̴̳̆o̵̎͜" or ctx.author.id == gl.my_user_id:
        output = " ".join(msg)
        await ctx.message.channel.edit(topic = output)
        await gl.update_ses('abyses', output)
        await ctx.send('--SESSION CHANGED--')
      else:
        await ctx.send(gl.no_gif)
        return
    await ctx.send(db['abyses'])

  @commands.command()
  async def update(self, ctx):
    if ctx.message.author.id == gl.my_user_id:
      await ctx.send("New features and/or commands added! Check out the site to see what's new.")
      await ctx.invoke(self.bot.get_command('help'))
    await ctx.message.delete()

  @commands.command()
  async def scan(self, ctx):
    async with ctx.typing():
      if ctx.message.author.id == gl.my_user_id:
        reactions_given = {}
        reactions_received = {}
        # example dictionary format
        # {
        #   CerealGuy69: {
        #     biglaff: 50,
        #     ses: 100
        #   }, Little_G: {
        #     biglaff: 100,
        #     ses: 50
        #   }
        # }
        async for msg in ctx.channel.history(limit=50000):
          for reaction in msg.reactions:
            # analyze reactions received
            author = msg.author.name
            # make sure emoji isnt a string, and assign to variable for simplicity
            if not isinstance(reaction.emoji, str):
              emoji = reaction.emoji.name
            else:
              continue
            if author in reactions_received:
              # user already in
              if emoji in reactions_received[author]:
                # user already has been reacted to with this emote, add to total
                reactions_received[author][emoji] += reaction.count
              else:
                # emote not documented, initialize to total
                reactions_received[author][emoji] = reaction.count
            else:
              # user not yet in reactions, initialize to emoji count
              reactions_received[author] = {emoji: reaction.count}

            # analyze reactions given
            async for reactor in reaction.users():
              if reactor.name in reactions_given:
                # user already reacted
                if emoji in reactions_given[reactor.name]:
                  # user already reacted with specific emoji
                  reactions_given[reactor.name][emoji] += 1
                else:
                  # reactor has not yet reacted with specific emoji
                  reactions_given[reactor.name][emoji] = 1
              else:
                # reactor has not yet reacted
                reactions_given[reactor.name] = {emoji: 1}

        # --Create Embeds--

        # map emoji names to their id's
        emojis = {}
        for emoji in ctx.guild.emojis:
          emojis[emoji.name] = emoji.id

        # create receieved emojis stat embed
        await self.create_embed(emojis, reactions_received, "received", ctx)

        # create given emojis stat embed
        await self.create_embed(emojis, reactions_given, "given", ctx)

      else:
        await ctx.send("We know we'd break the damn bot with everyone scanning")
        return await ctx.send(gl.finger_wag)

  async def create_embed(self, emojis, data, given_or_received, ctx):
    # same code for creating given and received emotes
    for user in data:
      embed = discord.Embed(
        title = "Emotes " + given_or_received.capitalize() + " Stats",
        description = "Amount of emotes " + given_or_received + " for " + user + " in " + str(ctx.channel.name),
        color = discord.Color.dark_green()
      )
      # get user avatar
      avatar = "https://www.biography.com/.image/t_share/MTE4MDAzNDEwNzg5ODI4MTEw/barack-obama-12782369-1-402.jpg" # default to Obama
      for member in ctx.guild.members:
        if member.name == user:
          avatar = member.avatar_url
      embed.set_author(name=user, icon_url=avatar)
      for emote in data[user]:
        emoji_string = "<" + ":" + emote + ":" + str(emojis[emote]) + ">"
        embed.add_field(name = emoji_string, value = data[user][emote])
      await ctx.send(embed=embed)

  @commands.command()
  async def inktober(self, ctx):
    today = date.today().day
    await ctx.send("Today's Inktober prompt is **" + self.inktober_prompts[int(today) - 1] + "**. Happy drawing!")