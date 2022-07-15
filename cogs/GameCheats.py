# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import sqlite3


class GameCheats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    owner_id = None
    db = sqlite3.connect('clown_db.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS clown_db (
        user_id BIGINT,
        lvl INT,
        money BIGINT,
        items_bought TEXT,
        item_equipped TEXT
    )""")

    async def get_owner_id(self):
        """Gets bot's owner id"""
        return (await self.bot.application_info()).owner.id

    def is_member_owner(self, member: discord.Member):
        """Checks whether the user is the owner of the bot"""
        return member.id == self.owner_id

    @commands.Cog.listener()
    async def on_ready(self):
        print('Game cheats have loaded!')
        self.owner_id = await self.get_owner_id()

    @commands.command(description="""Sets money to specified user. Only for bot's owner.""",
                      usage='set_lvl `discord_id` `money`')
    async def set_money(self, ctx, discord_id: int, money: int):
        """You can give money to anyone by using this command

        discord_id - ID of the user whose money will be changed \n
        money - amount of money
        """

        if not self.is_member_owner(ctx.author):
            await ctx.send(f'You cannot use it.')
            return

        self.sql.execute(f"SELECT user_id FROM clown_db WHERE user_id = {discord_id}")

        if self.sql.fetchone() is None:
            await ctx.send(f'The user with ID {discord_id} was not found')
            return

        if abs(money) > 1000000000:
            money = 1000000000

        self.sql.execute('UPDATE clown_db SET money = ? WHERE user_id = ?',
                         (money, discord_id))
        self.db.commit()

        await ctx.send(f'Successfully! User {discord_id} now has {money} money')

    @commands.command(description="""Sets max lvl to specified user. Only for bot's owner.""",
                      usage='set_lvl `discord_id` `lvl`')
    async def set_lvl(self, ctx, discord_id: int, max_lvl: int):
        """You can set a lvl of user by using this command

        discord_id - ID of the user whose level will be changed \n
        max_lvl - lvl you want
        """

        if not self.is_member_owner(ctx.author):
            await ctx.send('You cannot use it.')
            return

        self.sql.execute(f"SELECT user_id FROM clown_db WHERE user_id = {discord_id}")

        if self.sql.fetchone() is None:
            await ctx.send(f'The user with ID {discord_id} was not found')
            return

        if max_lvl > 10:
            max_lvl = 10
        if max_lvl < 1:
            max_lvl = 1

        self.sql.execute(f"UPDATE clown_db SET lvl = ? WHERE user_id = ?",
                         (max_lvl, discord_id))
        self.db.commit()

        await ctx.send(f'Successfully! User {discord_id} is on {max_lvl} lvl right now')

    @commands.command(description="""Sets equipped item to specified user. Made for fun. Only for bot's owner.""",
                      usage='set_lvl `discord_id` `item`')
    async def set_item(self, ctx, discord_id: int, item: str):
        """You can set a lvl of user by using this command

        discord_id - ID of the user whose level will be changed \n
        max_lvl - item you want to equip (can be any str)
        """

        if not self.is_member_owner(ctx.author):
            await ctx.send('You cannot use it.')
            return

        self.sql.execute(f"SELECT item_equipped FROM clown_db WHERE user_id = {discord_id}")

        if self.sql.fetchone() is None:
            await ctx.send(f'The user with ID {discord_id} was not found')
            return

        if len(item) > 1:
            item = item[0]

        self.sql.execute(f"UPDATE clown_db SET item_equipped = ? WHERE user_id = ?",
                         (item, discord_id))
        self.db.commit()

        await ctx.send(f'Successfully! User {discord_id} now has "{item}" item equipped')


def setup(bot: commands.Bot):
    bot.add_cog(GameCheats(bot))
