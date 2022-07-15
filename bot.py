import discord
from discord.ext import commands
import os
from config import prefix, token, enable_cheats

bot = commands.Bot(command_prefix=prefix)
bot.remove_command('help')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        await ctx.send(embed=discord.Embed(title='Error', description=error, color=discord.Colour.red()))


for filename in os.listdir('./cogs'):
    if not enable_cheats and filename.startswith('GameCheats'):
        continue
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
