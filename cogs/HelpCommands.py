# -*- coding: utf-8 -*-
import discord
from discord.ext import commands


class HelpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Help command has loaded!')

    @commands.command()
    async def help(self, ctx):
        """Helps user get info about bot"""
        embed = discord.Embed(title='HELP', color=ctx.author.color)
        embed.set_footer(text='Bot made by https://github.com/Murl1k')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/'
                                '922054558790868993/996734796657082478/Game_bot_avatar.png')

        if 'ClownGame' in self.bot.cogs:
            embed.add_field(name='\u200b', value='**GAME COMMAND**', inline=False)
            for command in self.bot.commands:
                if command.name == "clown":
                    embed.add_field(name=f'{command.name}', value=f'>>> {command.description}\n'
                                                                  f'**Usage: {command.usage}**', inline=False)

        if 'GameCheats' in self.bot.cogs:
            embed.add_field(name='\u200b', value='**CHEAT COMMANDS**', inline=False)

            for command in self.bot.commands:
                if command.name != "clown" and len(command.description) > 1:
                    embed.add_field(name=f'{command.name}', value=f'>>> {command.description}\n '
                                                                  f'**Usage: {command.usage}**', inline=False)

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(HelpCommands(bot))
