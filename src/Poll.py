import discord
from discord.ext import commands

class Poll(commands.Cog):
  # commands associated with the built-in poll function
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
  
  @commands.command()
  async def poll(self, ctx, *, args):
    try:
      # get the title
      poll_title = args[args.find('{') + 1:args.find('}')]
      args = args[args.find('['):]

      # get the arguments
      options = []
      while args:
        options.append(args[args.find('[') + 1:args.find(']')])
        args = args[args.find(']') + 2:] # +2 to account for bracket and white space
      
      # create embed
      embed = discord.Embed(
        title = poll_title,
        description = "React with emotes below to vote!",
        color = discord.Color.dark_green()
      )
      embed.set_author(name="Barack Obama", icon_url= "https://www.biography.com/.image/t_share/MTE4MDAzNDEwNzg5ODI4MTEw/barack-obama-12782369-1-402.jpg")
      counter = 1
      # await ctx.send("0\N{combining enclosing keycap}")
      for option in options:
        emoji_string = str(counter) + "\N{combining enclosing keycap}"
        embed.add_field(name = "Option " + emoji_string + ":", value = option, inline="False")
        counter += 1
      size = len(options)
      # check if poll only has 1 option to give snark
      if size == 1:
        embed.add_field(name = "Option 2\N{combining enclosing keycap}:", value = "Pollmaker is gey", inline="False")
      msg = await ctx.send(embed=embed)
      # add emojis
      for x in range(size):
        # x + 1 because it starts counting at 0
        emoji_string = str(x+1) + "\N{combining enclosing keycap}"
        await msg.add_reaction(emoji_string)
      if size == 1:
        await msg.add_reaction("2\N{combining enclosing keycap}")
      return
    except:
      await ctx.send("Poll was rigged. Reformat and try again")
      return