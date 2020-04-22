import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix = '!')

@client.command(name = 'load', hidden = True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send("loaded.")

@client.command(name = 'unload', hidden = True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send("unloaded.")

@client.command(name = 'reload', hidden = True)
@commands.is_owner()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send("reloaded.")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

#SUBOT
#token = 'NTA0NzQ5MDU2MDg2NzY5Njc1.XpYaQw.EQlbKmV1pKSHs86XV6aaGDyON2g'
#UMBC
token = "NTA0NzQ4NjQ4NzU2ODA1NjUy.Xopzfw.9PkX-zpOrGxnvmMykGzqXUTdoiE"
client.run(token)