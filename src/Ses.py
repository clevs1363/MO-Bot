import re
from replit import db
import globals as gl
from datetime import datetime
from pytz import timezone
from discord.ext import commands

class Ses(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
  
  @commands.command()
  async def ses(self, ctx, *msg):
    print(msg)
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
  async def sesdown(self, ctx):
    ses = db['ses']
    if ses:
      # get date
      date_match = re.search('([0-1][0-2]|[1-9])/([0-2][0-9]|[3][0-1]|[1-9])[/21]{0,1}', ses)
      if date_match:
        d = date_match.group(0) + "/21" if len(date_match.group(0)) == 5 else date_match.group(0)
        ses_day = datetime.strptime(d,"%m/%d/%y")
      else:
        return await ctx.send("The date could not be determined.")
      # get time
      ses_match = re.search('([0-9]|[0-1][0-2]):([0-5][0-9])\s*(am|pm)', ses)
      if ses_match:
        ses_time = ses_match.group(0).split(":")
        hour = int(ses_time[0])
        minute = int(ses_time[1][:1])
        if 'pm' in ses_time[1]:
          hour += 12
        hour -= 1
      else:
        return await ctx.send("The time could not be determined.")
      # format date and time into a datetime object
      tz = timezone('EST')
      final_date = datetime(ses_day.year, ses_day.month, ses_day.day, hour, minute, 0, tzinfo=tz)

      # get time delta
      countdown = final_date - datetime.now(tz=tz)
      # get elements of time delta
      count_days, count_hours, count_minutes = countdown.days, countdown.seconds//3600, (countdown.seconds//60)%60
      count_seconds = countdown.seconds - count_hours*3600 - count_minutes*60
      # build and send string
      ret_string = str(count_days) + " days, " + str(count_hours) + " hours, " + str(count_minutes) + " minutes, " + str(count_seconds) + " seconds until ses!!!!"
      await ctx.send(ret_string)
    else:
      await ctx.send("No ses scheduled yet!")

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
  
  