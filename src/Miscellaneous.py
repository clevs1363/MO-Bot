from discord.ext import commands
import datetime
import globals as gl
import discord
from replit import db
import matplotlib.pyplot as plt
import numpy as np
import collections
from io import BytesIO

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
        authors = []
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
            author = str(msg.author.id)
            if author not in authors:
              authors.append(author)
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
              reactor = str(reactor.id)
              if reactor not in authors:
                authors.append(reactor)
              if reactor in reactions_given:
                # user already reacted
                if emoji in reactions_given[reactor]:
                  # user already reacted with specific emoji
                  reactions_given[reactor][emoji] += 1
                else:
                  # reactor has not yet reacted with specific emoji
                  reactions_given[reactor][emoji] = 1
              else:
                # reactor has not yet reacted
                reactions_given[reactor] = {emoji: 1}

        # map emoji names to their id's
        emojis = {}
        for emoji in ctx.guild.emojis:
          emojis[emoji.name] = emoji.id
        
        # fill maps with default value 0
        for user in reactions_given:
          for emoji in emojis:
            if emoji not in reactions_given[user]:
              reactions_given[user][emoji] = 0
        for user in reactions_received:
          for emoji in emojis:
            if emoji not in reactions_received[user]:
              reactions_received[user][emoji] = 0
        
        # --Create MATPLOTS--

        # manually add bots
        user_map = db['user_map']
        user_map['887714761666600960'] = 'Obotoma Dev'
        user_map['887681266068111362'] = 'Obotma'

        for author in authors:
          author_name = db['user_map'][author]
          labels = sorted(emojis.keys())

          author_data_given = collections.OrderedDict(sorted(reactions_given[author].items()))
          author_data_received = collections.OrderedDict(sorted(reactions_received[author].items()))
          emojis_given = author_data_given.values()
          emojis_received = author_data_received.values()

          x = np.arange(len(labels))  # the label locations
          width = 0.35  # the width of the bars

          fig, ax = plt.subplots()
          print(x, len(emojis_given))
          rects1 = ax.bar(x - width/2, emojis_given, width, label='Given', color='#1c7da2')
          rects2 = ax.bar(x + width/2, emojis_received, width, label='Received', color='#f24b83')

          ax.set_ylabel('Number')
          ax.set_title('Emoji stats for ' + author_name)
          ax.set_xticks(x)
          ax.set_xticklabels(labels)
          ax.legend()
          ax.bar_label(rects1, padding=3)
          ax.bar_label(rects2, padding=3)

          fig.tight_layout()

          file = BytesIO()
          plt.savefig(file, format='png', bbox_inches="tight", dpi = 80)
          plt.close()
          file.seek(0)

          fname = "attachment://"+author_name+"stats.png"
          chart = discord.File(file,filename=fname)

          await ctx.send(file=chart)

        # create receieved emojis stat embed
        # await self.create_embed(emojis, reactions_received, "received", ctx)

        # create given emojis stat embed
        # await self.create_embed(emojis, reactions_given, "given", ctx)

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
    today = datetime.date.today().day
    await ctx.send("Today's Inktober prompt is **" + self.inktober_prompts[int(today) - 1] + "**. Happy drawing!")

  @commands.command(aliases=['whatday', 'whatdayisit'])
  async def day(self, ctx):
    cur_day = datetime.datetime.now()
    weekday = cur_day.strftime("%A")
    cur_date = cur_day.strftime("%x")
    return await ctx.send("Today is **" + weekday + "**, " + cur_date)
  
  @commands.command()
  async def secret_send(self, ctx, *text):
    channel_id = text[0]
    text_to_send = text[1:]
    channel = gl.bot.get_channel(int(channel_id))
    await channel.send(" ".join(text_to_send))
