import re
# from replit import db
import globals as gl
import asyncio
from datetime import datetime
from pytz import timezone
from discord.ext import commands, tasks

class Ses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    async def setup_hook(self):
        self.ses_reminder.start()

    @commands.command()
    async def ses(self, ctx, *msg):
        async with ctx.typing():
            await gl.add_emoji(ctx.message, 'ses', gl.bot.emojis)
            if msg:  # check if arguments were passed
                if ctx.author.id == gl.my_user_id:
                    output = " ".join(msg)
                    await ctx.message.channel.edit(topic=output)
                    await gl.update_ses('ses', output)
                    await ctx.send('--SESSION CHANGED--')
                else:
                    return await ctx.send(gl.no_gif)
            return await ctx.send(gl.db['ses'])

    @commands.command()
    async def presesdown(self, ctx):
        ses = await gl.get_emoji(ctx.guild, "ses")
        return await ctx.send("pre" + str(ses) + " rn")

    @commands.command()
    async def sesdown(self, ctx):
        await self.sesdown_(ctx, "ses")

    @commands.command()
    async def abysesdown(self, ctx):
        await self.sesdown_(ctx, "abyses")

    @commands.command()
    async def abyses(self, ctx, *msg):
        await gl.add_emoji(ctx.message, 'ses', gl.bot.emojis)
        if msg:  # check if arguments passed
            if ctx.author.id == gl.drew_id or ctx.author.id == gl.my_user_id:
                output = " ".join(msg)
                await ctx.message.channel.edit(topic=output)
                await gl.update_ses('abyses', output)
                await ctx.send('--SESSION CHANGED--')
            else:
                await ctx.send(gl.no_gif)
                return
        await ctx.send(gl.db['abyses'])

    async def sesdown_(self, ctx, which_ses):
        ses = gl.db[which_ses]
        if ses:
            # get date
            date_match = re.search(
                '([0-1][0-2]|[1-9])/([0-2][0-9]|[3][0-1]|[1-9])[/21]{0,1}',
                ses)
            if date_match:
                # print(date_match.group(0))
                # print(len(date_match.group(0)))
                d = None
                if len(date_match.group(0)) == 4:
                    d = "0" + date_match.group(0) + "/22"
                elif len(date_match.group(0)) == 5:
                    d = date_match.group(0) + "/22"
                elif len(date_match.group(0)) == 6:
                    d = date_match.group(0) + "22"
                else:
                    d = date_match.group(0)
                ses_day = datetime.strptime(d, "%m/%d/%y")
            else:
                return await ctx.send("The date could not be determined.")
            # get time
            ses_match = re.search('([0-9]|[0-1][0-2]):([0-5][0-9])\s*(am|pm)',
                                  ses)
            if ses_match:
                ses_time = ses_match.group(0).split(":")
                hour = int(ses_time[0])
                minute = int(ses_time[1][:1])
                if 'pm' in ses_time[1]:
                    hour += 12
            else:
                return await ctx.send("The time could not be determined.")
            # format date and time into a datetime object
            tz = timezone('EST')
            final_date = datetime(ses_day.year,
                                  ses_day.month,
                                  ses_day.day,
                                  hour,
                                  minute,
                                  0,
                                  tzinfo=tz)
            which_entry = which_ses + "_date"
            gl.db[which_entry] = {
              'year': ses_day.year,
              'month': ses_day.month,
              'day': ses_day.day,
              'hour': hour,
              'minute': minute,
              'seconds': 0
            }
            await gl.update_db()

            # get time delta
            countdown = final_date - datetime.now(tz=tz)
            # get elements of time delta
            count_days, count_hours, count_minutes = countdown.days, countdown.seconds // 3600, (
                countdown.seconds // 60) % 60
            count_seconds = countdown.seconds - count_hours * 3600 - count_minutes * 60
            # build and send string
            ret_string = str(count_days) + " days, " + str(
                count_hours) + " hours, " + str(
                    count_minutes) + " minutes, " + str(
                        count_seconds) + " seconds until " + which_ses + "!!!!"
            await ctx.send(ret_string)
            return count_days, count_hours, count_minutes, count_seconds
        else:
            await ctx.send("No " + which_ses + " scheduled yet!")
            return

    @tasks.loop(hours=336)
    async def ses_reminder(self):
        channel = gl.bot.get_channel(779693553092919306)  # dnd-campaign2
        dnd_role = "<@&862723344545742880>"
        # channel = gl.bot.get_channel(887682725375528963) # testing chat
        await channel.send(dnd_role + " ses in 8 hours!")
        await asyncio.sleep(25200)  # sleep for 7 hours
        await channel.send(dnd_role + " ses in 1 hour!!!")
        await asyncio.sleep(3000)  # sleep for 50 minutes
        await channel.send(dnd_role + " ses in 10 minutes!!!!!")

    @ses_reminder.before_loop
    async def before_ses_reminder(self):
        await gl.bot.wait_until_ready()
        if 'ses_date' not in gl.db.all():
            channel = gl.bot.get_channel(779693553092919306)  # dnd-campaign2
            channel.invoke(self.bot.get_command('sesdown'))
        # ses = db['ses_date']
        ses = gl.db["ses_date"]
        tz_ = timezone("EST")
        ses_date = datetime(ses['year'],
                            ses['month'],
                            ses['day'],
                            ses['hour'],
                            ses['minute'],
                            ses['second'],
                            tzinfo=tz_)
        cur_time = datetime.now(tz=tz_)
        ses_date.hours -= 8
        tdelta = (ses_date - cur_time)
        await asyncio.sleep(tdelta.seconds)

    @tasks.loop(hours=336)
    async def abyses_reminder(self):
        channel = gl.bot.get_channel(
            873264246622933013)  # dnd in suicide skwad 2
        dnd_role = "<@&899749981676793887>"  # @everyone
        # channel = gl.bot.get_channel(887682725375528963) # testing chat
        await channel.send(dnd_role + " abyses in 8 hours!")
        await asyncio.sleep(25200)  # sleep for 7 hours
        await channel.send(dnd_role + " abyses in 1 hour!!!")
        await asyncio.sleep(3000)  # sleep for 50 minutes
        await channel.send(dnd_role + " abyses in 10 minutes!!!!!")

    @abyses_reminder.before_loop
    async def before_abyses_reminder(self):
        await gl.bot.wait_until_ready()
        if 'ses_date' not in gl.db.all():
            channel = gl.bot.get_channel(873264246622933013)  # dnd
            channel.invoke(self.bot.get_command('abysesdown'))
        ses = gl.db["abyses_date"]
        tz_ = timezone("EST")
        ses_date = datetime(ses['year'],
                            ses['month'],
                            ses['day'],
                            ses['hour'],
                            ses['minute'],
                            ses['second'],
                            tzinfo=tz_)
        cur_time = datetime.now(tz=tz_)
        ses_date.hours -= 8
        tdelta = (ses_date - cur_time)
        await asyncio.sleep(tdelta.seconds)
