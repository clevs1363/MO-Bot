from discord.ext import commands
import globals as gl
import discord
from discord.abc import PrivateChannel
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
    if 'user_map' not in db.keys():
      db['user_map'] = {
        gl.drew_id: "Shroombo"
      }

  #
  # <-- TRIGGERED EVENTS -->
  #

  @gl.bot.event
  async def on_message(message):
    await gl.bot.process_commands(message)
    if message.author.bot:
      # ignore messages from bots
      return
    
    # add user to user_map if unknown
    if str(message.author.id) not in db['user_map']:
      db['user_map'][message.author.id] = message.author.name
      print('user_map is: ')
      print(db['user_map'])


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
      msg = re.sub(" *[\[\{\(-].*[\]\}\)-]", "", msg) # filters out [this text fools Obotma]
      add_stat = True
      last = None
      if re.search("[eE3£ᵉε🇪][rR][!?.]+$", msg) :
        # matches 1+ punctuation: pogger?, pogger!!!
        punc = msg[-1]
        last = (msg.split()[-1]).replace("?", "").replace('!', '').replace('.', '')
        await message.channel.send(responses[punc])
      elif re.search('([*][rR]+)(\W|\d|[_])*$', msg):
        last = msg.split()[-1]
        await message.channel.send("Censor? I 'ardly knew 'er!")
      elif re.search("([eE3£ᵉε🇪]([rR])+)(\W|\d|[_])*$", msg):
        # matches 1+ r's: pogger, poggerrrrr, poggerrrr*891832
        last = msg.split()[-1]
        span = re.search("([eE3£ᵉε🇪]([rR])+)(\W|\d|[_])*$", last).span()
        last = last.replace(" ", "")
        last_stripped = last[:span[0]+2] # removes excess symbols
        await message.channel.send(last_stripped + responses['default'])
      elif re.search("[eE3£ᵉε🇪][rR]\W+$", msg):
        # matches non-string characters at the end: pogger---, pogger###
        last = msg.split()[-1]
        span = re.search("[eE3£ᵉε🇪][rR]\W+$", last).span()
        last = last.replace(" ", "")
        last_stripped = last[:span[0]+2] # removes excess symbols
        await message.channel.send(last_stripped + responses['default'])
      elif re.search('[eE3£ᵉε🇪][rR]\d+$', msg):
        last = msg.split()[-1]
        span = re.search("[eE3£ᵉε🇪][rR]\d+$", last).span()
        last = last.replace(" ", "")
        last_stripped = last[:span[0]+2] # removes excess symbols
        await message.channel.send(last_stripped + responses['default'])
      else:
        add_stat = False

      if last:
        if last in db['hkr_words']:
          db['hkr_words'][last] += 1 
        else:
          db['hkr_words'][last] = 1

      if add_stat:
        if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, PrivateChannel):
          return await message.channel.send("What happens in private stays in private :)") 
        author_id = str(message.author.id)
        if str(message.author.id) != "887714761666600960" and str(message.author.id) != "439205512425504771":
          if author_id in db['hkr_stats']:
            db['hkr_stats'][author_id] += 1
          else:
            db['hkr_stats'][author_id] = 1

    # random fact
    fact_message = re.sub("<:[a-z]*:[0-9]{18}>", "", message.content) # ignore emotes of form <:emote:12439824598248> by substituting them with an empty string
    fact_message = re.sub("<@!*[0-9]{18}>", "", fact_message) # ignores user IDs (when @ed) of the form <@123456789123456789>
    fact_message = re.sub("<@&[0-9]{18}>", "", fact_message) # ignores roles (when @ed) of the form <@&123456789123456789>
    if '37' in fact_message and not message.content.startswith('https://'):
      return await gl.random_fact(message)

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
    if before.content == after.content:
      # ignore links, pins, etc., only editing message content
      return
    await gl.add_emoji(after, 'edited', gl.bot.emojis)
    if isinstance(after.channel, discord.DMChannel):
	    return await before.channel.send("What edits behind closed doors stays behind closed doors :)")
	  # ignore DMs adding stats 
    # add stats 
    author_id = str(before.author.id)
    if not before.author.bot:
      if author_id in db['edited_stats']:
        db['edited_stats'][author_id] += 1
      else:
        db['edited_stats'][author_id] = 1
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

  @gl.bot.event
  async def on_member_update(before, after):
    activity_type = None
    try:
      activity_type = after.activity.type
    except:
      pass
    if activity_type is discord.Streaming:
      # Do X if he is streaming
      channel = gl.bot.get_channel(604834176645988354)
      await channel.send(after.activity.twitch_name + 'is LIVE! Come in here or he\'ll come for your toes!' + '\n' + after.activity.name + '\n' + after.activity.url)
    else:
      pass

  @gl.bot.event
  async def on_reaction_add(reaction, user):
    if reaction.count == 5 and not isinstance(reaction.emoji, str) and reaction.emoji.name == "biglaff" and reaction.message.author.name == "Obotma":
      await reaction.message.reply("https://tenor.com/view/drop-the-mic-obama-mic-drop-gif-13109295")
    
    if reaction.count == 4 and reaction.emoji == "📌":
      await reaction.message.pin()
    
    if not isinstance(reaction.emoji, str) and reaction.emoji.name == "doot":
      await reaction.message.channel.send('Dute', tts=True)

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
    user_map = db['user_map']
    for user, num in data.items():
      if user in user_map:
        stat_heap.append((num, user_map[user]))
    counter = 1
    stat_heap = sorted(stat_heap, key=lambda a:a[0])
    stat_heap.reverse()
    ret_string = ""
    for stat in stat_heap:
      ret_string += str(counter) + ". **" + stat[1] + "**: " + str(stat[0]) + "\n"
      counter += 1
    return ret_string
  
  
