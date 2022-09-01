import asyncio
import requests
import discord
import random
import globals as gl
from datetime import date, datetime, timedelta
from pytz import timezone
from discord.ext import commands, tasks

class Schedule(commands.Cog):
  # commands and functions that occur at scheduled times
  def __init__(self, bot):
    self.bot = bot

  async def setup_hook(self):
    self.daily_message.start()

  @tasks.loop(hours=24)
  async def daily_message(self):
    channel = gl.bot.get_channel(604834176645988354) # chats and bants
    # channel = gl.bot.get_channel(887682725375528963) # testing chat
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
    r = requests.get("http://api.wordnik.com/v4/words.json/wordOfTheDay?api_key=" + gl.wordnik_key).json()
    word = r['word']
    defs_string = "" # string including all definitions
    definitions = r.get('definitions', [])
    if definitions:
      for definition in definitions:
        defs_string += "\N{bullet} *" + definition['partOfSpeech'] + "*. " + definition['text'] + "\n"
    ex_string = "" # string including one example
    examples = r.get('examples', [])
    if examples:
      ex_string += examples[0]['text']
    await channel.send('WORD OF THE DAY: ' + word)
    await channel.send(defs_string)
    await channel.send('\"' + ex_string + '\"')

    # send daily news
    await self.news(channel)

    # inktober52 link
    # await channel.send("See the following for Inktober52 prompts:\nhttps://inktober.com/inktober52")

  @daily_message.before_loop
  async def before_daily_message(self):
    hour = 8
    minute = random.randrange(15, 45)
    
    await gl.bot.wait_until_ready()
    tz = timezone('EST')
    now = datetime.now(tz)
    future = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    await asyncio.sleep((future-now).seconds)
  
  @commands.command()
  async def news(self, channel):
    # get current news
    topics = ['arts', 'automobiles', 'books', 'business', 'fashion', 'food', 'health', 'home', 'insider', 'magazine', 'movies', 'nyregion', 'obituaries', 'opinion', 'politics', 'realestate', 'science', 'sports', 'sundayreview', 'technology', 'theater', 't-magazine', 'travel', 'upshot', 'us', 'world']
    request_url = 'https://api.nytimes.com/svc/topstories/v2/' + random.choice(topics) + '.json?api-key=' + gl.nyt_key
    cur_r = requests.get(request_url).json()
    results = cur_r['results']
    cur_article = random.choice(results)
    embed = discord.Embed(
      title = cur_article['title'],
      description = cur_article['abstract'],
      color = discord.Color.darker_gray()
    )
    embed.add_field(name='Article link:', value=cur_article['url'])
    # get media thumbnail
    thumbnail = 'https://static01.nyt.com/vi-assets/images/share/1200x1200_t.png' # default value
    for media in cur_article['multimedia']:
      if media['type'] == 'image':
        if media['format'] == 'Standard Thumbnail':
          thumbnail = media['url']
    embed.set_author(name=cur_article['byline'], icon_url=thumbnail)
    await channel.send("Daily news:")
    await channel.send(embed=embed)

    # get popular news
    pop_r = requests.get('https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key=' + gl.nyt_key).json()
    results = pop_r['results']
    pop_article = random.choice(results)
    embed = discord.Embed(
      title = pop_article['title'],
      description = pop_article['abstract'],
      color = discord.Color.darker_gray()
    )
    embed.add_field(name='Article link:', value=pop_article['url'])
    # get media thumbnail
    thumbnail = 'https://static01.nyt.com/vi-assets/images/share/1200x1200_t.png' # default value
    for media in pop_article['media']:
      if media['type'] == 'image':
        if media['media-metadata'][0]['format'] == 'Standard Thumbnail':
          thumbnail = media['media-metadata'][0]['url']
    embed.set_author(name=pop_article['byline'], icon_url=thumbnail)
    await channel.send("Popular news:")
    await channel.send(embed=embed)
    await channel.send("If the above NYT links are paywalled, paste the link into this site (may try automating this soon): \nhttps://archive.ph/")
    