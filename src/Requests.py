from replit import db
from discord.ext import commands
import globals as gl

class Requests(commands.Cog):
  # commands associated with memes
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    if 'requests' not in db.keys():
      db['requests'] = {}
    if 'bugs' not in db.keys():
      db['bugs'] = []

  @commands.command(aliases=['req', 'requests'])
  async def request(self, ctx, *req):
    if req:
      if 'requests' in db.keys() and len(db['requests']) > 14:
        await ctx.send(gl.annoyed)
        return
      # add request to dictionary
      if 'requests' in db.keys():
        db['requests'][" ".join(req)] = ctx.message.author.id
      else:
        db['requests'] = {" ".join(req): ctx.message.author.id}
      await gl.add_emoji(ctx.message, "pepehap", gl.bot.emojis)
      await ctx.send("\U0001F60E" + "\U0001F44D")
      await ctx.send("You are number %s in the queue" % (len(db['requests'])))
    else:
      if 'requests' in db.keys() and db['requests']:
        # list requests
        ret_string = ""
        counter = 1
        for request, user in db['requests'].items():
          print(request, user)
          ret_string += str(counter) + '. ' + request
          ret_string += ' | *Requested by ' + db['user_map'][user] + '*\n'
          counter += 1
        await ctx.send(ret_string)
      else:
        # requests are empty
        await ctx.send("No features requested yet. Check the site to see what's in progress")
        await ctx.invoke(self.bot.get_command('help')) 
  
  @commands.command(aliases=['del_req', 'delete_requests', 'resolve_request'])
  async def delete_request(self, ctx, num):
    if int(num) == 0 and ctx.message.author.id == gl.my_user_id:
      # clear list
      if 'requests' in db:
        db['requests'] = {}
        await ctx.send("admin yoink")
      else:
        await ctx.send('nothing to admin yoink')
      return
    if 'requests' in db:
      counter = 1
      for request in db['requests'].keys():
        if counter == int(num):
          requester_id = db['requests'][request]
          if ctx.message.author.id == requester_id or ctx.message.author.id == gl.my_user_id:
            db['requests'].pop(request)
            await ctx.send("yoinked:\n> " + request + " | *Requested by " + db['user_map'][str(requester_id)] + "*")
          else:
            await ctx.send("Not very cash money of you to try and delete someone else's request")
            await ctx.send(gl.finger_wag)
        counter += 1
    else:
      await ctx.send('nothing to yoink yet')
  
  @commands.command(aliases=['bugs'])
  async def bug(self, ctx, *b):
    if b:
      # add bug to list
      await gl.add_emoji(ctx.message, "succ", gl.bot.emojis)
      db['bugs'].append(" ".join(b))
      await ctx.send("\U0001F912" + "\U0001F44D")
      await ctx.send("Bug number %s has been reported" % (len(db['bugs'])))
    else:
      if 'bugs' in db.keys() and db['bugs']:
        # list bugs
        bug_string = ""
        for index, bug in enumerate(db['bugs']):
          bug_string += str(index + 1) + ". " + bug + '\n'
        await ctx.send(bug_string)
      else:
        # no bugs to list
        await ctx.send("No bugs to smoosh right now")
  
  @commands.command(aliases=['res_bug', 'resolve_bugs', 'res_bugs'])
  async def resolve_bug(self, ctx, index):
    if ctx.message.author.id == gl.my_user_id:
      index = int(index)
      if index == 0:
        # clear list
        db['bugs'] = []
        return await ctx.send('Bugs smooshed.')
      else:
        if len(db['bugs']) > index:
          index -= 1 # normalize to start counting at 0
          # remove at index
          await gl.add_emoji(ctx.message, "partyparrot", gl.bot.emojis)
          resolved = db['bugs'].pop(index)
          return await ctx.send('Resolved: *' + resolved + '*')
        else:
          await gl.add_emoji(ctx.message, "angery", gl.bot.emojis)
          return await ctx.send('Format your index right, dumbass')
    else:
      return await ctx.send(gl.nope)

