from discord.ext import commands
import datetime
import globals as gl
import discord
from replit import db
import matplotlib
import matplotlib.pyplot as plt
# Customize matplotlib
matplotlib.rcParams.update(
  {
    'text.usetex': False,
    'font.family': 'stixgeneral',
    'mathtext.fontset': 'stix',
  }
)
import numpy as np
import collections
from io import BytesIO
from PIL import Image
from matplotlib.offsetbox import OffsetImage,AnnotationBbox
import math
import time

class Miscellaneous(commands.Cog):
  # Miscellaneous commands
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None

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
    await ctx.channel.send('KEEYILL', tts=True)
    return await ctx.send('https://www.youtube.com/watch?v=dyIilW_eBjc')

  @commands.command()
  async def update(self, ctx):
    if ctx.message.author.id == gl.my_user_id:
      await ctx.send("New features and/or commands added! Check out the site to see what's new.")
      await ctx.invoke(self.bot.get_command('help'))
    await ctx.message.delete()

  @commands.command()
  # uses global user map instead of dynamic db['user_map'] cuz I got rate limited by replit
  async def scan(self, ctx, channel=None):
    if not channel:
      scan_channel = ctx.channel
    else:
      scan_channel = gl.bot.get_channel(int(channel))
    async with ctx.typing():
      if ctx.message.author.id == gl.my_user_id:
        timer = time.perf_counter()
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
        num_msgs_sent = {}
        async for msg in scan_channel.history(limit=100000):
          # collect data about messages sent per user 
          author = str(msg.author.id)
          if author not in gl.user_map:
            continue
          if author in num_msgs_sent:
            num_msgs_sent[author] += 1
          else:
            num_msgs_sent[author] = 1

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
        
        # fill emojis with now-lost emotes
        for r in reactions_given:
          for e in reactions_given[r]:
            if e not in emojis:
              emojis[e] = 0 # placeholder ID of 0
        for r in reactions_received:
          for e in reactions_received[r]:
            if e not in emojis:
              emojis[e] = 0 # placeholder ID of 0
        
        # fill maps with default value 0
        for user in reactions_given:
          for emoji in emojis:
            if emoji not in reactions_given[user]:
              reactions_given[user][emoji] = 0
        for user in reactions_received:
          for emoji in emojis:
            if emoji not in reactions_received[user]:
              reactions_received[user][emoji] = 0 
        
        emojis = collections.OrderedDict(sorted(emojis.items())) # sort by emoji name to make alphabetical

        # --Create MATPLOTS--

        # manually add bots
        # user_map = db['user_map']
        # user_map['887714761666600960'] = 'Obotoma Dev'
        # user_map['887681266068111362'] = 'Obotma'
        # user_map['439205512425504771'] = 'NotSoBot'

        # lock channel
        # await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        # bot_member = ctx.guild.get_member(gl.bot.user.id)
        # bot_role = bot_member.roles[0]
        # await ctx.channel.set_permissions(bot_role, send_messages=True)

        for author in authors:
          if author not in reactions_given or author not in reactions_received:
            continue 
          author_name = db['user_map'][author]
          labels = sorted(emojis.keys())

          author_data_given = collections.OrderedDict(sorted(reactions_given[author].items()))
          author_data_received = collections.OrderedDict(sorted(reactions_received[author].items()))
          emojis_given = author_data_given.values()
          emojis_received = author_data_received.values()

          # x = np.arange(len(labels))  # the label locations
          # width = 0.35  # the width of the bars

          # # debugging incompatible size error
          # # print(labels)
          # # print(len(labels))
          # # print(reactions_given)
          # # print(len(reactions_given))
          # # print(reactions_received)
          # # print(len(reactions_received))

          # fig, ax = plt.subplots(figsize=(27, 15), dpi=100)
          # rects1 = ax.bar(x - width/2, emojis_given, width, label='Given', color='#1c7da2')
          # rects2 = ax.bar(x + width/2, emojis_received, width, label='Received', color='#f24b83')

          # ax.set_ylabel('Number')
          # ax.set_title('Emoji stats for ' + author_name)
          # ax.set_xticks(x)
          # ax.set_xticklabels(labels)
          # plt.xticks(rotation=45, ha='right') # rotate labels
          # plt.tick_params(axis='x', which='major', pad=25) # space out x labels
          # fig.subplots_adjust(bottom=0.2)
          # ax.legend()
          # ax.bar_label(rects1, padding=3)
          # ax.bar_label(rects2, padding=3)

          # for i, c in enumerate(emojis):
          #   await self.offset_image(i, c, ax, ctx.guild.emojis) 

          # fig.tight_layout()

          # file = BytesIO()
          # plt.savefig(file, format='png', bbox_inches="tight", dpi = 100)
          # plt.close()
          # file.seek(0)

          # fname = "attachment://"+author_name+"stats.png"
          # chart = discord.File(file,filename=fname)

          # await ctx.send("<@" + author + "> :", file=chart)
        
        # send emojis-per-message stats
        emote_stats_to_get = ['sens', 'wetawd', 'rocc', 'smurk', 'yes', 'withered', 'edited', 'ses', 'biglaff']
        for emote_name in emote_stats_to_get:
          # proportion of emote given 
          custom_emoji = await gl.get_emoji(ctx.guild, emote_name)
          rates_given = await self.emojis_per_message(num_msgs_sent, reactions_given, emote_name, custom_emoji, "gave")
          await ctx.send("**Ratio rankings of " + str(custom_emoji) + "s given per message:**")
          await ctx.send(rates_given)
          # proportion of emote given 
          rates_received = await self.emojis_per_message(num_msgs_sent, reactions_received, emote_name, custom_emoji, "received")
          await ctx.send("**Ratio rankings of " + str(custom_emoji) + "s received per message:**")
          await ctx.send(rates_received)

        # unlock channel
        # await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        
        final_timer = time.perf_counter() - timer
        await ctx.send("*Scan time taken: " + str(math.floor(final_timer/60)) + " minutes, " + str(round(timer%60, 2)) + " seconds*")

        # create receieved emojis stat embed
        # await self.create_embed(emojis, reactions_received, "received", ctx)

        # create given emojis stat embed
        # await self.create_embed(emojis, reactions_given, "given", ctx)

      else:
        await ctx.send("We know we'd break the damn bot with everyone scanning")
        return await ctx.send(gl.finger_wag)

  async def get_emoji_img(self, emojis, name):
    for emoji in emojis:
      if emoji.name == name:
        emoji_file = await emoji.url.read()
        # resize image
        img = Image.open(BytesIO(emoji_file))
        width, height = img.size
        size = width/4, height/4
        img.thumbnail(size, Image.ANTIALIAS)
        # save into readable bytes file
        bytes_file = BytesIO()
        img.save(bytes_file, "PNG")
        bytes_file.seek(0)
        img = bytes_file.read()
        final_im = plt.imread(BytesIO(img), format='raw')
        return final_im
    # if emoji not found, send a default image
    default_img = plt.imread('docs/assets/default.png')
    return default_img

  async def offset_image(self, coord, name, ax, emojis):
    img = await self.get_emoji_img(emojis, name)
    im = OffsetImage(img, zoom=0.72)
    im.image.axes = ax

    ab = AnnotationBbox(im, (coord, 0),  xybox=(0., -16.), frameon=False, xycoords='data',  boxcoords="offset points", pad=0)

    ax.add_artist(ab) 
  
  async def emojis_per_message(self, msgs_sent, reactions, emoji_name, custom_emoji, given_or_received):
    rates = []
    for user_id in msgs_sent:
      if user_id not in gl.user_map or user_id not in reactions or user_id not in msgs_sent:
        continue
      rate = reactions[user_id][emoji_name] / msgs_sent[user_id]
      rates.append((gl.user_map[user_id], rate))
    rates.sort(key=lambda y: y[1]) # sort by second value of tuple (rate)
    rates.reverse()
    ret_string = ""
    for index, user_rate in enumerate(rates, start=1):
      ret_string += "**" + str(index) + ".** " + user_rate[0] + ": " + given_or_received + " a " + emoji_name + " on " + str(round(user_rate[1]*100, 2)) + "% of messages\n"
      if user_rate[1] != 0:
        ret_string += "(" + given_or_received + " a " + str(custom_emoji) + " every " + str(math.ceil(1/user_rate[1])) + " messages)\n"
    return ret_string

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
    return await ctx.send("Inktober is over, but see the following for Inktober52 prompts:\nhttps://inktober.com/inktober52")

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

  @commands.command()
  async def study(self, ctx):
    return await ctx.send("https://www.youtube.com/watch?v=ZBojGJGJAgQ&ab_channel=ThomasMiller")
