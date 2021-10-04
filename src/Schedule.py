import asyncio
import requests
import random
import globals as gl
from datetime import date, datetime, timedelta
from pytz import timezone
from discord.ext import commands, tasks

class Schedule(commands.Cog):
  # commands and functions that occur at scheduled times
  def __init__(self, bot):
    self.bot = bot
    self.daily_message.start()

  @tasks.loop(hours=24)
  async def daily_message(self):
    channel = gl.bot.get_channel(604834176645988354) # chats and bants
    # channel = bot.get_channel(887682725375528963) # testing chat
    await channel.send("Good morning.")

    # send today in history
    # API docs: https://history.muffinlabs.com/
    today = date.today().strftime("%m/%d/%y").split("/")
    month = today[0]
    day = today[1]
    fact_request = requests.get("http://history.muffinlabs.com/date/%s/%s" % (month, day)).json()["data"]

    event_fact = fact_request["Events"][0]
    event_links = " | ".join(["<" + link['link'] + ">" for link in event_fact['links']])
    birth_fact = fact_request['Births'][0]
    birth_links = " | ".join(["<" + link['link'] + ">" for link in birth_fact['links']])
    death_fact = fact_request["Deaths"][0]
    death_links = " | ".join(["<" + link['link'] + ">" for link in death_fact['links']])

    await channel.send("TODAY IN HISTORY: \n")
    await channel.send("\N{bullet} %s: %s \n" % (event_fact['year'], event_fact['text']))
    await channel.send(event_links)
    await channel.send("\N{bullet} %s is born. %s" % (birth_fact['text'], birth_links))
    await channel.send("\N{bullet} %s dies. %s" % (death_fact['text'], death_links))

    # send quote of the day
    # API docs: https://github.com/lukePeavey/quotable
    quote_response = requests.get("https://api.quotable.io/random").json()
    quote = quote_response['content']
    author = quote_response['author']
    await channel.send("QUOTE OF THE DAY: \"%s\" \n~%s" % (quote, author))

    # send definition of the day
    url = "https://wordsapiv1.p.rapidapi.com/words/"
    querystring = {"random":"true"}
    headers = {
      'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
      'x-rapidapi-key': "fb731cefd2msh69364977b49898ep16b903jsn21c4ae1a6eab"
    }

    # API is very inconsistent, loop until getting a valid word
    all_fields = False
    while not all_fields:
      r = requests.request("GET", url, headers=headers, params=querystring).json()
      if 'word' not in r or 'results' not in r:
        pass
      else:
        all_fields = True

    try:
      word = "\N{bullet}".join([syllable for syllable in r['syllables']['list']]) # join syllables over dot like google definition
    except:
      word = r['word'] # revert to default word if syllables not present
    pronunciation = "[none]"
    if 'pronunciation' in r and 'all' in r['pronunciation']:
      pronunciation = r['pronunciation']['all']
    definitions = "\n\N{bullet}".join([definition['definition'] for definition in r['results']])

    await channel.send("WORD OF THE DAY: %s" % word)
    await channel.send(pronunciation)
    await channel.send("\N{bullet}" + definitions)

  @daily_message.before_loop
  async def before_daily_message(self):
    hour = 7
    minute = random.randrange(15, 45)
    await gl.bot.wait_until_ready()
    tz = timezone('EST')
    now = datetime.now(tz) 
    future = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    await asyncio.sleep((future-now).seconds)