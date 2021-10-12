from discord.ext import commands
import globals as gl
import discord
import re
import asyncio
import random
from replit import db

class Text(commands.Cog):
  # commands and events associated with messages and their contents
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    # if 'requests' in db.keys():
    #   del db['requests']
    if 'hkr_stats' not in db.keys():
      db['hkr_stats'] = {}
    if 'edited_stats' not in db.keys():
      db['edited_stats'] = {}

  #
  # <-- TRIGGERED EVENTS -->
  #

  @gl.bot.event
  async def on_message(message):
    await gl.bot.process_commands(message)
    if message.author.bot:
      # ignore messages from bots
      return

    if isinstance(message.channel, discord.DMChannel):
      if message.author.id != gl.my_user_id:
        m = gl.bot.get_user(gl.my_user_id)
        await m.send(f"*Message from {message.author}*:\n{message.content}")

    # hkh, ignores links and commands
    if not message.clean_content.startswith('https://') and not message.clean_content.startswith('!'):
      # TODO: tidy up this code
      responses = {
        '.': "...I 'ardly knew 'er.",
        '?': "I 'ardly knew 'er!",
        "!": "Aha! I did in fact know 'er!",
        'default': "? I 'ardly knew 'er!"
      }
      msg = re.sub("<:[a-z]*:[0-9]{18}>", "", message.content) # filters out emoji
      add_stat = True
      if re.search("[eE3£ᵉε]r[!?.]+$", msg) :
        # matches 1+ punctuation: pogger?, pogger!!!
        punc = msg[-1]
        last = (msg.split()[-1]).replace("?", "").replace('!', '').replace('.', '')
        await message.channel.send(responses[punc])
      elif re.search('([*]r+)(\W|\d|[_])*$', msg):
        await message.channel.send("Censor? I 'ardly knew 'er!")
      elif re.search("([eE3£ᵉε](r)+)(\W|\d|[_])*$", msg):
        # matches 1+ r's: pogger, poggerrrrr, poggerrrr*891832
        last = msg.split()[-1]
        span = re.search("([eE3£ᵉε](r)+)(\W|\d|[_])*$", last).span()
        last_stripped = last[:span[0]+2] # removes excess symbols
        await message.channel.send(last_stripped + responses['default'])
      elif re.search("[eE3£ᵉε]r\W+$", msg):
        # matches non-string characters at the end: pogger---, pogger###
        last = msg.split()[-1]
        span = re.search("[eE3£ᵉε]r\W+$", last).span()
        last_stripped = last[:span[0]+2] # removes excess symbols
        await message.channel.send(last_stripped + responses['default'])
      elif re.search('[eE3£ᵉε]r\d+$', msg):
        last = msg.split()[-1]
        span = re.search("[eE3£ᵉε]r\d+$", last).span()
        last_stripped = last[:span[0]+2] # removes excess symbols
        await message.channel.send(last_stripped + responses['default'])
      else:
        add_stat = False
      
      if add_stat:
        author = message.author.name
        if author != 'Obotma Dev' and author != 'NotSoBot':
          if author in db['hkr_stats']:
            db['hkr_stats'][author] += 1
          else:
            db['hkr_stats'][author] = 1

    # random fact
    fact_message_1 = re.sub("<:[a-z]*:[0-9]{18}>", "", message.content) # ignore emotes of form <:emote:12439824598248> by substituting them with an empty string
    fact_message = re.sub("<@!*[0-9]{18}>", "", fact_message_1) # ignores user IDs (when @ed) of the form <@123456789123456789>
    if '37' in fact_message and not message.content.startswith('https://'):
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
    if 'https://' in before.content:
      # ignore links
      return
    await gl.add_emoji(after, 'edited', gl.bot.emojis)
    # add stats 
    author = before.author.name
    if author != 'Obotma Dev' and author != 'NotSoBot':
      if author in db['edited_stats']:
        db['edited_stats'][author] += 1
      else:
        db['edited_stats'][author] = 1
    # if before.author.id == gl.drew_id:
    #   # harass drew
    #   messages = ['Did you have to edit that message?', 'I see you.', 'You\'ve been testing me...it\'s time I test you.', 'Go edit boy go', 'I see every edit you made...', 'You hate me because of :edited:. But despite my ghoulish reputation, I really have the heart of a small boy. I keep it in a jar in my server room.', 'Hell is empty and all the edits are here.', 'Yeeees...edit that message...', 'The message was fine before.', 'Was that necessary', 'Get :edited:']
    #   edited = [emoji for emoji in before.guild.emojis if emoji.name == 'edited']
    #   if edited:
    #     edited = edited[0]
    #     drew = gl.bot.get_user(gl.drew_id)
    #     await drew.send(random.choice(messages))
    #     await drew.send(edited)
    #     return # exit if not found

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
      hkr_string = await self.get_stats(db['hkr_stats'])
      await ctx.send('How many times has everyone been *hardly knew er*-ed?\n' + hkr_string)
    if not db['edited_stats']:
      await ctx.send('No edited stats yet!')
    else:
      edited_string = await self.get_stats(db['edited_stats'])
      await ctx.send('How many times has everyone edited?\n' + edited_string)

  async def get_stats(self, data):
    # data should be a dictionary
    stat_heap = []
    for user, num in data.items():
      if user != "Obotma Dev" and user != "NotSoBot":
        stat_heap.append((num, user))
    counter = 1
    stat_heap = sorted(stat_heap, key=lambda a:a[0])
    stat_heap.reverse()
    ret_string = ""
    for stat in stat_heap:
      ret_string += str(counter) + ". **" + stat[1] + "**: " + str(stat[0]) + "\n"
      counter += 1
    return ret_string
      
  