import globals as gl
import math
import ast
import operator as op
import functools
from discord.ext import commands

class Math(commands.Cog):
  # wrapper function for ast and other math operations
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.xor, ast.BitXor: op.pow, ast.USub: op.neg}

  @commands.command(aliases = ['math', 'eval'])
  async def m(self, ctx, *expr):
      """
      >>> eval_expr('2^6')
      4
      >>> eval_expr('2**6')
      64
      >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
      -5.0
      """
      expr = "".join(expr)
      eval_ = self.limit(max_=10**1000)(self.eval_)
      try:
        result = eval_(ast.parse(expr, mode='eval').body)
        return await ctx.send(result)
      except ValueError:
        return await ctx.send("Result too thicc. Make smaller")

  def eval_(self, node):
    if isinstance(node, ast.Num): # <number>
        return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return self.operators[type(node.op)](self.eval_(node.left), self.eval_(node.right))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return self.operators[type(node.op)](self.eval_(node.operand))
    else:
        raise TypeError(node)
    
  def limit(self, max_=None):
    def decorator(func):
      @functools.wraps(func)
      def wrapper(*args, **kwargs):
          ret = func(*args, **kwargs)
          try:
              mag = abs(ret)
          except TypeError:
              pass # not applicable
          else:
              if mag > max_:
                raise ValueError(ret)
          return ret
      return wrapper
    return decorator
  
  @commands.command()
  async def cos(self, ctx, num):
    parsed_num = self.eval_(ast.parse(num, mode='eval').body)
    return await ctx.send(math.cos(parsed_num))
  
  @commands.command()
  async def sin(self, ctx, num):
    parsed_num = self.eval_(ast.parse(num, mode='eval').body)
    return await ctx.send(math.sin(parsed_num))
  
  @commands.command()
  async def tan(self, ctx, num):
    parsed_num = self.eval_(ast.parse(num, mode='eval').body)
    return await ctx.send(math.tan(parsed_num))
