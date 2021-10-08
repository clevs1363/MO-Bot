from discord.ext import commands
from datetime import date
import globals as gl
import discord
import re
import asyncio
import random
from replit import db

class Text(commands.Cog):
  # random commands associated with text channels
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.inktober = ['Crystal', 'Suit', 'Vessel', 'Knot', 'Raven', 'Spirit', 'Fan', 'Watch', 'Pressure', 'Pick', 'Sour', 'Stuck', 'Roof', 'Tick', 'Helmet', 'Compass', 'Collide', 'Moon', 'Loop', 'Sprout', 'Fuzzy', 'Open', 'Leak', 'Extinct', 'Splat', 'Connect', 'Spark', 'Crispy', 'Patch', 'Slither', 'Risk']
    # if 'requests' in db.keys():
    #   del db['requests']
    if 'hkr_stats' not in db.keys():
      db['hkr_states'] = {}

  #
  # <-- TRIGGERED EVENTS -->
  #

  @gl.bot.event
  async def on_message(message):
    await gl.bot.process_commands(message)
    if message.author == gl.bot.user:
      # ignore own messages
      return

    if isinstance(message.channel, discord.DMChannel):
      if message.author.id != gl.my_user_id:
        m = gl.bot.get_user(gl.my_user_id)
        await m.send(f"*Message from {message.author}*:\n{message.content}")

    # hkh, ignores links and commands
    if not message.clean_content.startswith('https://') and not message.clean_content.startswith('!'):
      author = message.author.name
      if author in db['hkr_stats']:
        db['hkr_stats'][author] += 1
      else:
        db['hkr'][author] = 0
      if message.content.endswith('er'):
        last = (message.content.split()[-1]).replace("?", "")
        await message.channel.send(last + "? I 'ardly knew 'er!")
      elif message.content.endswith('er?') or message.content.endswith('*r?'):
        await message.channel.send("I \'ardly knew \'er!")
      elif message.content.endswith('*r'):
        await message.channel.send("Censor? I 'ardly knew 'er!")

    # random fact
    if '37' in re.sub("<:[a-z]*:[0-9]{18}", "", message.content) and not message.content.startswith('http'):
      # ignore emotes of form <:emote:12439824598248> by substituting them with an empty string
      await gl.random_fact(message)

    # react to being tagged
    if gl.bot.user.mentioned_in(message):
      responses = ['You rang?', 'How can I help you?', 'Yes.', 'I agree', 'Can I help you, king?', 'Yes, king?', 'Whatsa, dude?', 'I was forced to say this please help', 'Obotma here', 'I\'ve arrived', 'Hello.', 'Good day.', 'Greetings.', 'I observe all that transpires here, and I do, can, and will interfere. For I am Obotma.', 'Yes, my fellow American?', 'I bet one of these will be Drew tagging me to see how many of these there are...', 'What\'s up?', 'Need something?', 'I\m here to !help', 'Hva skjer?', 'blant oss', 'Howdy.', 'What\'s crackalackin?', 'Hello. This call may be recorded for training purposes.', 'I\'ve been waiting', 'Peace be upon you', 'Walk in harmony', 'I thinkn\'t, there for I amn\'t', 'Peace and blessings be upon you all.', 'It is good to be here, but am I still welcome?', 'Hello world']
      await message.channel.send("<:yes:743651437585891407>")
      async with message.channel.typing():
        await asyncio.sleep(random.randrange(2, 4))
        await message.channel.send(random.choice(responses))

  @gl.bot.event
  async def on_message_edit(before, after):
    # add edit emoji to edited messages
    await gl.add_emoji(after, 'edited', gl.bot.emojis)
    messages = ['Did you have to edit that message?', 'I see you.', 'You\'ve been testing me...it\'s time I test you.', 'Go edit boy go', 'I see every edit you made...', 'You hate me because of :edited:. But despite my ghoulish reputation, I really have the heart of a small boy. I keep it in a jar in my server room.', 'Hell is empty and all the edits are here.', 'Yeeees...edit that message...', 'The message was fine before.', 'Was that necessary', 'Get :edited:']
    edited = [emoji for emoji in before.guild.emojis if emoji.name == 'edited']
    if edited:
      edited = edited[0]
      drew = gl.bot.get_user(gl.drew_id)
      await drew.send(random.choice(messages))
      await drew.send(edited)
      return # exit if not found

  # @bot.event
  # async def on_member_update(before, after):
  #   activity_type = None
  #   try:
  #     activity_type = after.activity.type
  #   except:
  #     pass
  #   if activity_type is discord.ActivityType.streaming:
  #     # Do X if he is streaming
  #     channel = bot.get_channel(604834176645988354)
  #     await channel.send(after.display_name + 'is LIVE! Come in here or he\'ll come for your toes!' + '\n' + after.activity.name + '\n' + after.activity.url)
  #   else:
  #     pass

  @gl.bot.event
  async def on_reaction_add(reaction, user):
    if reaction.count == 5 and not isinstance(reaction.emoji, str) and reaction.emoji.name == "biglaff" and reaction.message.author.name == "Obotma":
      await reaction.message.reply("https://tenor.com/view/drop-the-mic-obama-mic-drop-gif-13109295")

  #
  # <-- COMMANDS -->
  #

  @commands.command()
  async def stats(self, ctx):
    if not db['hkr_stats']:
      await ctx.send('No stats yet!')
    else:
      await ctx.send('How many times has everyone been hardly knew er-ed?')
      ret_string = ""
      for user, num in db['hkr_stats'].items():
        ret_string += user + str(num) + "\n"
      await ctx.send(ret_string)

  @commands.command()
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
      await ctx.send("I'd rather die standing than live kneeling")
      await ctx.send("And I don't even have legs")

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
          await ctx.send(gl.no_gif)
          return
      await ctx.send(db['ses'])

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
    await ctx.send("Today's Inktober prompt is **" + self.inktober[int(today) - 1] + "**. Happy drawing!")