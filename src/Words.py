import asyncio
import requests
import random
import globals as gl
from discord.ext import commands
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

class Words(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
  
  @commands.command()
  async def define(self, ctx, word, num=1):
    async with ctx.typing():
      if num > 3:
        await ctx.send("Hell, I'll do it, but *sheeesh*...")
      elif num < 1:
        await ctx.send("Nice try Drew")
        return
      r = requests.get("https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=" + gl.mw_dict_key).json()[0]
      if 'shortdef' in r and r['shortdef']:
        # checks to make sure definitions exist and are nonempty
        definitions = r['shortdef']
        ret_string = word + ": *" + r.get('fl', "") + "*\n" # get label if it exists
        for i, definition in enumerate(definitions):
          ret_string += "**" + str(i+1) + ".** " + definition + "\n"
        examples = r.get('suppl', '')
        print("examples: " + examples)
        if examples:
          example = r.get(examples['examples'][0]['t'], '')
          ret_string += '*Example*: ' + example
        return await ctx.send(ret_string)
      else:
        return await ctx.send("No definitions found. Maybe try !udefine, that guy has some wacky shit...")
    
  @commands.command(aliases=['synonyms'])
  async def syns(self, ctx, word, depth=1):
    async with ctx.typing():
      if depth > 3:
        await ctx.send("Hell, I'll do it, but *sheeesh*...")
      elif depth < 1:
        await ctx.send("Nice try Drew")
        return
      r = requests.get("https://www.dictionaryapi.com/api/v3/references/thesaurus/json/" + word + "?key=" + gl.mw_thes_key).json()[0]
      if r['meta'] and 'syns' in r['meta'] and r['meta']['syns']:
        # checks to make sure definitions exist and are nonempty
        definitions = r['meta']['syns']
        syn_string = "**" + word + "**: *" + r.get('fl', "") + "*\n" # get label if it exists
        syn_string += '*Synonyms*: '
        for i in range(min(depth, len(definitions))):
          syn_string += ", ".join(definitions[i])
        await ctx.send(syn_string)
        # get antonyms
        if 'ants' in r['meta'] and r['meta']['ants']:
          antonyms = r['meta']['ants']
          ant_string = '*Antonyms*: '
          for i in range(min(depth, len(antonyms))):
            ant_string += ', '.join(antonyms[i])
          await ctx.send(ant_string)
        return
      else:
        return await ctx.send("No synonyms found.")
  
  @commands.command(aliases=['urban_define'])
  async def udefine(self, ctx, word, num=1):
    # num is amount of definitions to return
    if num > 5:
      await ctx.send("Max 5 definitions please")
      return
    elif num < 1:
      await ctx.send("Nice try Drew")
      return
    # urban dictionary definition
    url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
    querystring = {"term": word}
    headers = {
      'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
      'x-rapidapi-key': "fb731cefd2msh69364977b49898ep16b903jsn21c4ae1a6eab"
    }
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    definitions = response['list'] # list of dictionaries
    if definitions:  
      async with ctx.typing():
        num_definitions = len(definitions)
        for d in range(num):
          if not d > num_definitions:
            # send message
            cur_def = definitions[d]
            definition = cur_def['definition'].replace("[", "").replace("]", "")
            await ctx.send(definition)
            up_rate = (int(cur_def['thumbs_up']) / (int(cur_def['thumbs_up']) + int(cur_def['thumbs_down']))) * 100
            up_rate = round(up_rate, 2)  # percentage thumbs-upped to 4 decimal points
            await ctx.send("\N{thumbs up sign}: **" + str(cur_def['thumbs_up']) + "**  \N{thumbs down sign}: **" + str(cur_def['thumbs_down']) + "**  (" + str(up_rate) + "% upvoted)")
        else:
          return
    else:
      return await ctx.send("No definitions found. Go add it yourself, king \n https://www.urbandictionary.com/")
    
  @commands.command()
  async def freq_dist(self, ctx, num=3):
    if ctx.author.id != gl.my_user_id:
      return await ctx.send("Access denied")
    if num > 10:
      return await ctx.send("max of 10 plz, gonna toast my cpu")
    async with ctx.typing():
      tokenized_words = []
      tokenizer = nltk.RegexpTokenizer(r"[a-zA-Z]+") # ignores punctuation

      # get all messages
      async for msg in ctx.channel.history(limit=100000):
        removes_punc = tokenizer.tokenize(msg.clean_content)
        tokenized_words.extend(removes_punc)

      # remove stop words
      stop_words=set(stopwords.words("english"))
      filtered_sent=[]
      for w in tokenized_words:
        if w not in stop_words:
          filtered_sent.append(w)
      # ps = PorterStemmer()
      # stemmed_words=[]
      # for w in filtered_sent:
      #   stemmed_words.append(ps.stem(w))

      fdist = FreqDist(filtered_sent)
      ret_string = ""
      for count, word in enumerate(fdist.most_common(num), start=1):
        ret_string += str(count) + ". **" + word[0] + "**: " + str(word[1]) + "\n"
      return await ctx.send(ret_string)