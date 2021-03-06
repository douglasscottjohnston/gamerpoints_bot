import os
import pickle
import discord
import discord.ext
from discord.ext import commands
from dotenv import load_dotenv

from SaveBoard import SaveBoard


# todo: put on the server and add a database to store the points and users, also fix the add and remove points functions




#Credentials
load_dotenv('.env')
GAMERPOINTS_BOT_TOKEN = os.getenv("GAMERPOINTS_BOT_TOKEN")

#Intents
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='-',intents=intents)

#Global variables
scoreboard = {} # member : score

#SQLite
save = SaveBoard(scoreboard)

  #messeges
notInMsg = " is not in the scoreboard, add them with the add_user command"
inMsg = " is already in the scoreboard"

#Commands
@bot.command(name="add_server", description="Adds the entire server to the scoreboard")
@commands.has_permissions(administrator=True)
async def add_server(ctx):
  for guild in bot.guilds:
    for member in guild.members:
      if not member.bot:
        await add_user(ctx, member)

@bot.command(name="add_user", description="Adds a member to the scoreboard")
@commands.has_permissions(administrator=True)
async def add_user(ctx, *members: commands.Greedy[discord.Member]):
  scoreboard = save.load_obj()
  for member in members:
    if member.name in scoreboard:
      await ctx.send(member.name + inMsg)
    else:
      scoreboard[member.name] = 0
      save.save_obj(scoreboard)
      await ctx.send(member.name + " added with a score of 0")

@bot.command(name="remove_user", description="Removes a member from the scoreboard")
@commands.has_permissions(administrator=True)
async def remove_user(ctx, *members: commands.Greedy[discord.Member]):
  scoreboard = save.load_obj()
  for member in members:
    if member.name in scoreboard:
      del scoreboard[member.name]
      await ctx.send(member.name + " removed from the scoreboard")
    else:
      await ctx.send(member.name + notInMsg)
  save.save_obj(scoreboard)

@bot.command(name="won_game", description="Adds 10 points to all members that won a game")
async def won_game(ctx, *members: commands.Greedy[discord.Member]):
  scoreboard = save.load_obj()
  print(scoreboard)
  for member in members:
    if member.name in scoreboard:
      scoreboard[member.name] = scoreboard.get(member.name) + 10
      await ctx.send(member.name + " gained 10 gamerpoints!")
    else:
      await ctx.send(member.name + notInMsg)
  save.save_obj(scoreboard)

@bot.command(name="lost_game", description="Removes 10 points from all members that lost a game")
async def lost_game(ctx, *members: commands.Greedy[discord.Member]):
  scoreboard = save.load_obj()
  for member in members:
    if member.name in scoreboard:
      scoreboard[member.name] = scoreboard.get(member.name) - 10
      await ctx.send(member.name + " lost 10 gamerpoints!")
    else:
      await ctx.send(member.name  + notInMsg)
  save.save_obj(scoreboard)

@bot.command(name="add_points", description="Adds points to the member")
@commands.has_permissions(administrator=True)
async def add_points(ctx, *, member, points):
  scoreboard = save.load_obj()
  if member.name in scoreboard:
    scoreboard[member.name] = scoreboard.get(member.name) + points
    await ctx.send(member.name + (" gained %d gamerpoints!" % points))
  else:
    await ctx.send(member + notInMsg)
  save.save_obj(scoreboard)

@bot.command(name="remove_points", description="Removes points from tmember")
@commands.has_permissions(administrator=True)
async def remove_points(ctx, *, member, points):
  scoreboard = save.load_obj()
  if member.name in scoreboard:
    scoreboard[member.name] = scoreboard.get(member.name) - points
    await ctx.send(member + " lost %d gamerpoints" % points)
  else:
    await ctx.send(member + notInMsg)
  save.save_obj(scoreboard)

@bot.command(name="scores", description="Displays the scoreboard")
async def scores(ctx):
  scoreboard = save.load_obj()
  bWidth = 32 #board width
  uWidth = 14 #width of the user section
  sWidth = 15 #width of the score section
  row = ('-' * bWidth)
  row += "\n| place | user:  score\n"#14 lines in user, 15 lines in score, 32 total
  place = 1
  for member, points in sorted(scoreboard.items(), key=lambda item: item[1], reverse=True):
  #generates the place of each user
    row += "|"
    row += ((" %s |") % place)
  #generates the user portion of the scoreboard
    #puts in the optimal ammount of spaces
    spaces = (' ' * int((uWidth - len(member)) / 2))
    row += spaces
    row += member
    row += ":"
    row += spaces
  #generates the score part of the scoreboard
    spoints = str(points)
    #maxes out the score at 999999999999999 if the score is bigger than the sWidth
    if len(spoints) > sWidth:
      row += ('9' * sWidth)
    #inserts no spaces if the score has as many digets as the width
    elif len(spoints) == sWidth:
      row += spoints
    #puts the optimal ammount of spaces for any score bigger with multiple digets
    elif len(spoints) > 9:
      spaces = (' ' * int((sWidth - len(spoints)) / 2))
      row += spaces
      row += spoints
      row += spaces
    else:
      row += (' ' * 7)
      row += spoints
      row += (' ' * 7)
    place += 1
    row += "\n"
  row += ('-' * bWidth)
  print(row)
  #sends the scoreboard as an embed in the channel
  msg = discord.Embed(title="Gamerpoints Leaderboard", description=row)
  await ctx.send(embed=msg)
  

#Events
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(Message):
    await bot.process_commands(Message)







bot.run(os.getenv('GAMERPOINTS_BOT_TOKEN'))
