# -*- coding: utf-8 -*-
import discord
import asyncio
from discord_components import *
from discord.ext import commands
import sqlite3


class ClownGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.bot)
        print('Game has loaded!')

    db = sqlite3.connect('clown_db.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS clown_db (
        user_id BIGINT,
        lvl INT,
        money BIGINT,
        items_bought TEXT,
        item_equipped TEXT
    )""")

    clown_online_list = []

    def get_clown_online(self):
        return len(self.clown_online_list)

    @commands.command(description="""Main game. Here you need to help clown find the disk.
                       You can also get more money by getting a golden disk.""",
                      usage='clown')
    async def clown(self, ctx):
        """Main game function"""

        if ctx.message.author.id in self.clown_online_list:
            await ctx.send(embed=discord.Embed(title='You cannot play multiple games at the same time',
                                               colour=discord.Colour.red()))
            return
        else:
            self.clown_online_list.append(ctx.message.author.id)

        def disable_buttons(buttons_):
            for button_list in buttons_:
                for button in button_list:
                    button.set_disabled(True)

        message = await ctx.send(f'Launching game for {ctx.author.mention}')

        async def menu():
            """ Start menu """
            start_buttons = [
                [Button(style=ButtonStyle.gray, label=f'Current Online: {self.get_clown_online()}', disabled=True)],
                [Button(style=ButtonStyle.green, label='Play')],
                [Button(style=ButtonStyle.blue, label=f'Shop')],
                [Button(style=ButtonStyle.blue, label=f'Inventory')],
                [Button(style=ButtonStyle.red, label='Exit')]
            ]

            await message.edit(f"{ctx.author.mention}'s game", components=start_buttons)

            close_game = False

            while True:
                try:
                    inter = await self.bot.wait_for('button_click',
                                                    check=lambda i: i.author == ctx.message.author,
                                                    timeout=30)
                except asyncio.TimeoutError:

                    disable_buttons(start_buttons)
                    await message.edit('\u200b', components=start_buttons)
                    self.clown_online_list.remove(ctx.message.author.id)
                    return

                label = inter.component.label

                if label == start_buttons[1][0].label:
                    try:
                        await inter.respond(type=6)
                        close_game = await lvl_chooser()

                    except discord.NotFound:
                        continue

                elif label == start_buttons[2][0].label:
                    try:
                        await inter.respond(type=6)
                        close_game = await shop()

                    except discord.NotFound:
                        continue

                elif label == start_buttons[3][0].label:
                    try:
                        await inter.respond(type=6)
                        close_game = await inventory()

                    except discord.NotFound:
                        continue

                elif label == start_buttons[4][0].label:
                    disable_buttons(start_buttons)
                    await message.edit(f"{ctx.author.mention}'s game", components=start_buttons)
                    await inter.respond(type=6)

                    self.clown_online_list.remove(ctx.message.author.id)
                    return

                if close_game:
                    return

                await message.edit(f"{ctx.author.mention}'s game", components=start_buttons)

        async def shop():
            """Here you can buy skins"""
            nonlocal money
            nonlocal items_bought

            shop_items = {
                '😈': 100,
                '😍': 110,
                '😊': 130,
                '😘': 150,
                '💩': 190,
                '😵': 130,
                '🤐': 120,
                '😻': 150,
                '😎': 120,
                '😭': 130,
                '🐶': 150,
                '🐷': 200
            }

            shop_buttons = [[Button(style=ButtonStyle.blue, label='Shop', disabled=True),
                             Button(style=ButtonStyle.blue, label=f'Your balance: {money}', disabled=True),
                             Button(style=ButtonStyle.red, label='Back', custom_id='back')]]

            # Removes purchased items from the list
            for skin in list(shop_items):
                if skin in items_bought:
                    del shop_items[skin]

            shop_buttons_in_row = []

            for item in shop_items.items():
                shop_buttons_in_row.append(Button(style=ButtonStyle.gray,
                                                  label=item[1],
                                                  emoji=f'{item[0]}')
                                           )

            # Splitting the list into lists of 3 elements
            shop_buttons_in_row = [shop_buttons_in_row[i:i + 3] for i in range(0, len(shop_buttons_in_row), 3)]

            for row_of_buttons in shop_buttons_in_row:
                shop_buttons.append(row_of_buttons)

            await message.edit(f"{ctx.author.mention}'s game", components=shop_buttons)

            while True:
                try:
                    inter = await self.bot.wait_for('button_click',
                                                    check=lambda i: i.author == ctx.message.author,
                                                    timeout=30)

                except asyncio.TimeoutError:
                    disable_buttons(shop_buttons)
                    await message.edit(f'\u200b', components=shop_buttons)
                    self.clown_online_list.remove(ctx.message.author.id)

                    return True

                if inter.component.custom_id == 'back':
                    await inter.respond(type=6)

                    return False

                price = int(inter.component.label)

                if price > money:
                    try:
                        await inter.respond(type=6)
                        continue
                    except discord.NotFound:
                        continue

                else:
                    try:
                        await inter.respond(type=6)

                        money -= price
                        items_bought += inter.component.emoji.name

                        self.sql.execute(f"UPDATE clown_db SET items_bought = ?, money = ? WHERE user_id = ?",
                                         (f"{items_bought}", money, ctx.message.author.id))
                        self.db.commit()

                        return False
                    except discord.NotFound:
                        pass

        async def inventory():
            """Here you can equip your skins"""
            nonlocal items_bought
            nonlocal item_equipped

            inventory_buttons = [[Button(style=ButtonStyle.green, label='Inventory', disabled=True),
                                  Button(style=ButtonStyle.red, label='Back', custom_id='back')]]

            inventory_items = [Button(style=ButtonStyle.gray, emoji='🤡')]

            if items_bought != '':
                for item in items_bought:
                    inventory_items.append(Button(style=ButtonStyle.gray, emoji=item))

            # Makes equipped item's button disabled
            for button in inventory_items:
                if item_equipped == button.emoji.name:
                    button.set_disabled(True)

            # Splitting the list into lists of 3 elements
            inventory_items = [inventory_items[i:i + 5] for i in range(0, len(inventory_items), 5)]

            for row in inventory_items:
                inventory_buttons.append(row)

            await message.edit(f"{ctx.author.mention}'s", components=inventory_buttons)

            while True:

                try:
                    inter = await self.bot.wait_for('button_click',
                                                    check=lambda i: i.author == ctx.message.author,
                                                    timeout=30)

                except asyncio.TimeoutError:
                    disable_buttons(inventory_buttons)
                    await message.edit(f'\u200b', components=inventory_buttons)
                    self.clown_online_list.remove(ctx.message.author.id)

                    return True

                if inter.component.custom_id == 'back':
                    await inter.respond(type=6)

                    return False

                try:
                    await inter.respond(type=6)

                    item_equipped = inter.component.emoji.name

                    self.sql.execute(f"UPDATE clown_db SET item_equipped = ? WHERE user_id = ?",
                                     (f"{item_equipped}", ctx.message.author.id))
                    self.db.commit()

                    return False

                except discord.NotFound:
                    pass

        async def lvl_chooser():
            """Here you can choose a lvl"""

            lvl_access = [True, True, True, True, True, True, True, True, True, True]

            # Makes it impossible to complete levels that have not been completed
            for n in range(0, lvl_max):
                lvl_access[n] = False

            lvl_buttons = [
                [Button(style=ButtonStyle.green, label='Choose a lvl', disabled=True),
                 Button(style=ButtonStyle.red, label='Back')],

                [Button(style=ButtonStyle.gray, label='1', disabled=lvl_access[0]),
                 Button(style=ButtonStyle.gray, label='2', disabled=lvl_access[1]),
                 Button(style=ButtonStyle.gray, label='3', disabled=lvl_access[2]),
                 Button(style=ButtonStyle.gray, label='4', disabled=lvl_access[3]),
                 Button(style=ButtonStyle.gray, label='5', disabled=lvl_access[4])],

                [Button(style=ButtonStyle.gray, label='6', disabled=lvl_access[5]),
                 Button(style=ButtonStyle.gray, label='7', disabled=lvl_access[6]),
                 Button(style=ButtonStyle.gray, label='8', disabled=lvl_access[7]),
                 Button(style=ButtonStyle.gray, label='9', disabled=lvl_access[8]),
                 Button(style=ButtonStyle.gray, label='10', disabled=lvl_access[9])]
            ]

            lvl_display_button = lvl_buttons[0][0]

            await message.edit(f"{ctx.author.mention}'s game", components=lvl_buttons)

            while True:
                try:
                    inter = await self.bot.wait_for('button_click',
                                                    check=lambda i: i.author == ctx.message.author,
                                                    timeout=30)

                except asyncio.TimeoutError:
                    lvl_display_button.set_label("You didn't have time to choose a level")
                    disable_buttons(lvl_buttons)
                    await message.edit(f'\u200b', components=lvl_buttons)

                    self.clown_online_list.remove(ctx.message.author.id)

                    return True

                lvl = inter.component.label

                if lvl == lvl_buttons[0][1].label:
                    try:
                        await inter.respond(type=6)
                        return False

                    except discord.NotFound:
                        continue

                else:
                    try:
                        await inter.respond(type=6)
                    except discord.NotFound:
                        continue
                    await game(lvl)
                    return True

        async def game(lvl):
            """Main game"""
            nonlocal money
            nonlocal lvl_max

            player_model = item_equipped
            brown_square = '🟫'
            green_square = '⬛'
            treasure = '💿'
            dislike_emoji = '👎🏾'
            like_emoji = '👍🏾'
            dislike_emoji_1 = '👎'
            like_emoji_1 = '👍'
            snail_emoji = '🐌'
            outbox_red = "📤"
            outbox_green = '📥'
            green_wall = '🟩'
            golden_disk_emoji = '📀'
            cherry_emoji = '🍒'
            carrot_emoji = "🥕"
            rabbit_emoji = '🐇'
            locked_emoji = '🔒'
            unlocked_emoji = '🔓'
            white_square = '⬜'
            green_circle = '🟢'

            async def message_edit():
                await message.edit(f"{ctx.author.mention}'s game \n" + ''.join(space))

            async def interact_response():
                await inter.respond(type=6)

            def check_n_conditions():
                """
                Checks whether the player has entered the wall that is on the line transfer
                """
                return player_model_condition in n_conditions

            def activator(lock_condition: int, lever_condition: int, _activated: bool, player_condition: int,
                          emoji=like_emoji):
                """

                You need to go to the lever to remove the created wall.

                lock_condition: wall's cord \n
                lever_condition: lever's cord \n
                _activated: bool \n
                player_condition: player's cord \n
                emoji: lever's emoji after activation \n
                """

                emoji_switch_conditions = [lever_condition - 1, lever_condition + 1, lever_condition + 14,
                                           lever_condition - 14]

                if player_condition == lock_condition and not _activated:
                    player_condition = old_player_condition

                elif player_condition in emoji_switch_conditions and not _activated:
                    _activated = True
                    space[lock_condition] = green_square
                    space[lever_condition] = emoji

                elif player_condition == lever_condition:
                    player_condition = old_player_condition

                return player_condition, _activated

            def chooser(lock_condition: int, false_item_condition: int, true_item_condition: int, picked_item: list,
                        player_condition: int, false_item_emoji=cherry_emoji, true_item_emoji=carrot_emoji,
                        lock_emoji=rabbit_emoji):
                """

                To open the wall you need to pick up truly item and bring it to the wall. If you bring the fake one,
                game will be lost.

                lock_condition: wall's cord \n
                false_item_condition: fake item's cord \n
                true_item_condition: truly item's cord \n
                picked_item: list of 3 boolean ([False, False, False]) \n
                player_condition: player's cord \n
                false_item_emoji: fake item's emoji\n
                true_item_emoji: truly item's emoji \n
                lock_emoji wall's emoji \n
                """
                if not picked_item[2]:
                    around_lock = [lock_condition - 1, lock_condition + 1, lock_condition + 14, lock_condition - 14]

                    if not picked_item[1] and player_condition == lock_condition:
                        player_condition = old_player_condition

                    elif picked_item[0] and player_condition in around_lock:
                        display_button.set_label(f"{lock_emoji} doesn't eat {false_item_emoji}!")
                        display_button.set_style(ButtonStyle.red)

                        raise StopIteration

                    elif picked_item[1] and player_condition in around_lock:

                        picked_item[2] = True
                        space[lock_condition] = green_square

                    elif player_condition == false_item_condition:

                        if picked_item[1]:
                            space[true_item_condition] = true_item_emoji
                            picked_item[1] = False

                        picked_item[0] = True

                    elif player_condition == true_item_condition:

                        if picked_item[0]:
                            space[false_item_condition] = false_item_emoji
                            picked_item[0] = False

                        picked_item[1] = True

                return player_condition, picked_item

            def double_activator(lock_condition_1: int, lock_condition_2: int, lever_condition: int, _activated: bool,
                                 player_condition: int, emoji_locked=locked_emoji, emoji_unlocked=unlocked_emoji,
                                 wall_emoji=white_square):
                """

                You can go only through one wall, to open another one you need to go to the lock.

                lock_condition_1: first wall's cord \n
                lock_condition_2: second wall's cord \n
                lever_condition: lock's cord \n
                _activated: bool \n
                player_condition: player's cord \n
                emoji_locked: lock's emoji when locked \n
                emoji_unlocked: lock's emoji when unlocked \n
                wall_emoji: wall's emoji
                """

                emoji_switch_conditions = [lever_condition - 1, lever_condition + 1, lever_condition + 14,
                                           lever_condition - 14]

                if (player_condition == lock_condition_1 and not _activated) or \
                        (player_condition == lock_condition_2 and _activated):

                    player_condition = old_player_condition

                elif player_condition in emoji_switch_conditions and not _activated:

                    _activated = True

                    space[lock_condition_2] = wall_emoji
                    space[lock_condition_1] = green_square
                    space[lever_condition] = emoji_unlocked

                elif player_condition in emoji_switch_conditions and _activated:

                    _activated = False

                    space[lock_condition_1] = wall_emoji
                    space[lock_condition_2] = green_square
                    space[lever_condition] = emoji_locked

                elif player_condition == lever_condition:

                    player_condition = old_player_condition

                return player_condition, _activated

            def double_door(lever_1: int, lever_2: int, door_cord: list, _activated: list, player_condition: int,
                            lever_1_emoji=green_circle, lever_2_emoji=green_circle):
                """

                It's like an activator, but you need to activate 2 levers to open the wall.

                lever_1: first lever's cord \n
                lever_2: second lever's cord \n
                door_cord: cord list of walls \n
                _activated: bool list([False, False]) \n
                player_condition: player's cord \n
                lever_1_emoji: first lever's emoji \n
                lever_2_emoji: second lever's emoji
                """

                lever_switch_1 = [lever_1 - 1, lever_1 + 1, lever_1 + 14, lever_1 - 14]
                lever_switch_2 = [lever_2 - 1, lever_2 + 1, lever_2 + 14, lever_2 - 14]

                if player_condition in lever_switch_1 and not _activated[0]:
                    space[lever_1] = lever_1_emoji
                    _activated[0] = True

                elif player_condition in lever_switch_2 and not _activated[1]:
                    space[lever_2] = lever_2_emoji
                    _activated[1] = True

                if player_condition in [lever_1, lever_2]:
                    player_condition = old_player_condition

                elif player_condition in door_cord and (not _activated[0] or not _activated[1]):
                    player_condition = old_player_condition

                if _activated[0] and _activated[1]:
                    for cord in door_cord:
                        space[cord] = green_square

                return player_condition, _activated

            def space_changer(switcher_cord: int, new_player_condition: int, treasure_cord: int, new_space: list,
                              new_walls_conditions: list, player_condition: int, _activated: bool,
                              bonus_cord: int = None):
                """

                Changes the whole space when you go into the specified coordinate.

                switcher_cord: specified coordinate \n
                new_player_condition: new player's cord(if you need to change it) \n
                treasure_cord: treasure's place \n
                new_space: list of new space \n
                new_walls_conditions: list of new walls \n
                player_condition: player's cord \n
                _activated: bool \n
                bonus_cord: cord of bonus(if exists)
                """

                nonlocal treasure_condition
                nonlocal bonus_condition

                if player_condition == switcher_cord and not _activated:
                    space[:] = new_space
                    if new_walls_conditions:
                        walls_conditions[:] = new_walls_conditions
                    treasure_condition = treasure_cord
                    player_condition = new_player_condition
                    if bonus_cord:
                        bonus_condition = bonus_cord
                    _activated = True

                return player_condition, _activated

            def generate_space(start_player_condition: int = None, bonus_condition_: int = None,
                               treasure_condition_: int = 0, walls_: list = None, special_models_: list = None):
                """

                Generates a world and walls.

                start_player_condition: start player's cord \n
                bonus_condition_: cord of bonus disk \n
                treasure_condition_: treasure's place \n
                walls_: list of walls \n
                special_models_: specific dict of models \n
                """

                new_space = [brown_square, brown_square, brown_square, brown_square, brown_square, brown_square,
                             brown_square,
                             brown_square, brown_square, brown_square, brown_square, brown_square, brown_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, green_square, green_square, green_square, green_square, green_square,
                             green_square,
                             green_square, green_square, green_square, green_square, green_square, green_square,
                             brown_square + '\n',
                             brown_square, brown_square, brown_square, brown_square, brown_square, brown_square,
                             brown_square,
                             brown_square, brown_square, brown_square, brown_square, brown_square, brown_square,
                             brown_square + '\n']

                permanent_walls_conditions = []

                for element_index, elem in enumerate(new_space):
                    if elem == brown_square or elem == brown_square + '\n':
                        permanent_walls_conditions.append(element_index)

                if walls_ is not None:
                    for wall in walls_:
                        new_space[wall] = brown_square

                    walls_ = permanent_walls_conditions + walls_

                else:
                    walls_ = permanent_walls_conditions

                if special_models_ is not None:
                    for models in special_models_:
                        for model in models.items():
                            new_space[model[1]] = model[0]

                if bonus_condition_ is not None:
                    new_space[bonus_condition_] = golden_disk_emoji

                if start_player_condition is not None:
                    new_space[start_player_condition] = player_model

                if treasure_condition_ != 0:
                    new_space[treasure_condition_] = treasure

                return new_space, walls_

            """
            Default settings
            """
            def check_lvl_conditions(cord=int, activated_=list):
                """

                In this function we will put obstacles

                cord: player's cord \n
                activated_: list of boolean
                """
                return cord, activated_

            # Also default settings
            activated = []
            treasure_condition = 26
            player_model_condition = 15
            bonus_condition = 0
            walls = []
            special_models = []
            bonus_collected = False
            money_for_lvl = 0

            """We will change the settings depending on the level"""
            if lvl == '1':
                money_for_lvl = 10
                player_model_condition = 169
                treasure_condition = 26
                bonus_condition = 102

                walls = [16, 17, 18, 21, 22, 23, 24, 25, 34, 35, 44, 46, 47, 48, 51, 52, 53, 54, 57, 58, 60, 64, 65, 71,
                         76, 77, 78, 79, 80, 82, 85, 87, 88, 89, 90, 93, 94, 96, 99, 101, 107, 113, 115, 116, 117, 118,
                         119, 121, 122, 124, 127, 141, 143, 144, 146, 147, 148, 149, 152, 155, 157, 160, 161, 162, 163,
                         164, 165, 166]

            elif lvl == '2':
                walls = [30, 32, 33, 35, 36, 38, 39, 44, 48, 51, 53, 58, 60, 62, 72, 74, 75, 76, 78, 79, 80, 81, 82, 89,
                         92, 99, 100, 102, 103, 104, 105, 106, 108, 109, 110, 119, 122, 128, 133, 136, 142, 143, 144,
                         145,
                         147, 150, 158, 161, 162, 164, 166, 172]

                player_model_condition = 85
                treasure_condition = 90
                bonus_condition = 180

                money_for_lvl = 20

            elif lvl == '3':
                def check_lvl_conditions(cord: int, activated_: list):

                    cord, activated_[0] = activator(23, 54, activated_[0], cord)

                    return cord, activated_

                money_for_lvl = 30
                bonus_condition = 45
                walls = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 44, 48, 50, 51, 52, 53, 58, 59, 60, 62, 64, 66, 67,
                         76,
                         78, 81, 86, 87, 88, 89, 90, 92, 95, 100, 114, 115, 116, 120, 123, 130, 131, 132, 133, 134, 135,
                         138, 141, 145, 148, 151, 165, 170, 173, 175]

                special_models = [
                    {snail_emoji: 23},
                    {dislike_emoji: 54}
                ]
                activated = [False]

            elif lvl == '4':
                def check_lvl_conditions(cord: int = player_model_condition, activated_=list):

                    cord, activated[0] = activator(18, 51, activated[0], cord)
                    cord, activated[1] = activator(151, 107, activated[1], cord, emoji=like_emoji_1)
                    cord, activated[2] = activator(128, 180, activated[2], cord, emoji=outbox_green)

                    return cord, activated_

                money_for_lvl = 40
                walls = [30, 31, 32, 33, 34, 35, 36, 37, 38, 52, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 86, 87, 88, 89,
                         90,
                         91, 92, 93, 94, 108, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 142, 143, 144, 145, 146,
                         147, 148, 149, 150, 152, 162, 163, 176, 177]

                player_model_condition = 15
                treasure_condition = 178
                bonus_condition = 161

                special_models = [
                    {'🐌': 18},
                    {dislike_emoji: 51},
                    {'👎': 107},
                    {'🟩': 128},
                    {'🐌': 151},
                    {'🕹': 180}
                ]
                activated = [False, False, False]

            elif lvl == '5':
                money_for_lvl = 50

                def check_lvl_conditions(cord: int, activated_: list):

                    cord, activated_[0] = activator(36, 151, activated_[0], cord)
                    cord, activated_[1] = activator(162, 180, activated_[1], cord, emoji=like_emoji_1)
                    cord, activated_[2] = activator(73, 134, activated_[2], cord, emoji=outbox_green)

                    return cord, activated_

                bonus_condition = 46
                walls = [17, 29, 31, 32, 33, 34, 35, 37, 38, 39, 40, 45, 48, 49, 51, 57, 59, 60, 62, 65, 67, 76, 77, 81,
                         85, 87, 88, 89, 90, 94, 101, 107, 110, 113, 119, 120, 121, 122, 124, 129, 130, 131, 132, 133,
                         135, 141, 147, 149, 157, 158, 159, 160, 161, 163, 164, 165, 166]
                special_models = [{snail_emoji: 36},
                                  {green_wall: 73},
                                  {outbox_red: 134},
                                  {dislike_emoji: 151},
                                  {snail_emoji: 162},
                                  {dislike_emoji_1: 180}]

                activated = [False, False, False]

            elif lvl == '6':
                def check_lvl_conditions(cord: int, activated_: list):

                    cord, activated_[0] = activator(79, 53, activated_[0], cord, emoji=like_emoji_1)
                    cord, activated_[1] = activator(123, 161, activated_[1], cord)
                    cord, activated_[2] = activator(86, 180, activated_[2], cord, emoji=outbox_green)
                    cord, activated_[3] = chooser(103, 127, 131, activated_[3], cord)

                    return cord, activated_

                money_for_lvl = 60
                walls = [21, 30, 31, 32, 35, 37, 38, 39, 40, 46, 47, 48, 49, 51, 60, 65, 74, 85, 87, 88, 89, 90, 91, 92,
                         93,
                         107, 113, 114, 116, 117, 118, 121, 122, 124, 128, 130, 132, 142, 144, 146, 147, 148, 156, 158,
                         160,
                         162, 174]

                player_model_condition = 99
                treasure_condition = 26
                bonus_condition = 34
                special_models = [{'👎': 53}, {'🐌': 79}, {'🟩': 86}, {'🐇': 103}, {'🐌': 123}, {'🍒': 127},
                                  {'🥕': 131}, {dislike_emoji: 161}, {'📤': 180}]

                activated = [False, False, False, [False, False, False]]

            elif lvl == '7':
                def check_lvl_conditions(cord: int, activated_: list):

                    cord, activated_[0] = activator(46, 20, activated_[0], cord, emoji=like_emoji_1)

                    cord, activated_[1] = activator(115, 86, activated_[1], cord)

                    cord, activated_[2] = activator(173, 169, activated_[2], cord, emoji=outbox_green)

                    cord, activated_[3] = chooser(52, 124, 62, activated_[3], cord)

                    return cord, activated_

                money_for_lvl = 70
                walls = [19, 21, 35, 43, 44, 45, 47, 48, 49, 50, 51, 53, 54, 61, 63, 64, 68, 72, 73, 75, 77, 87, 89, 99,
                         100, 101, 103, 104, 105, 106, 109, 117, 123, 128, 129, 131, 135, 136, 137, 138, 143, 149, 157,
                         159,
                         160, 161, 162, 163, 165, 171, 179]

                player_model_condition = 15
                treasure_condition = 26
                bonus_condition = 180

                special_models = [{'👎': 20}, {'🐌': 46}, {'🐇': 52}, {'🥕': 62}, {dislike_emoji: 86}, {'🐌': 115},
                                  {'🍒': 124},
                                  {'📤': 169}, {'🟩': 173}]

                activated = [False, False, False, [False, False, False]]

            elif lvl == '8':
                def check_lvl_conditions(cord: int, activated_: list):

                    cord, activated_[0] = double_activator(62, 132, 89, activated_[0], cord)
                    cord, activated_[1] = activator(148, 23, activated_[1], cord)
                    cord, activated_[2] = activator(174, 180, activated_[2], cord, emoji=like_emoji_1)
                    cord, activated_[3] = activator(53, 127, activated_[3], cord, emoji=outbox_green)
                    cord, activated_[4] = chooser(109, 121, 43, activated_[4], cord)

                    return cord, activated_

                money_for_lvl = 80
                walls = [22, 24, 25, 26, 30, 31, 32, 33, 34, 36, 38, 44, 48, 50, 52, 54, 57, 58, 66, 76, 77, 78, 79, 80,
                         90,
                         104, 105, 106, 107, 108, 110, 113, 114, 118, 120, 128, 134, 138, 142, 146, 151, 152, 156, 157,
                         158,
                         159, 160, 162, 176, 177, 178, 179]

                player_model_condition = 85
                treasure_condition = 91
                bonus_condition = 40

                special_models = [{dislike_emoji: 23}, {'🥕': 43}, {'🟩': 53}, {'⬜': 62}, {'🔒': 89},
                                  {'🐇': 109}, {'🍒': 121}, {'📤': 127}, {'🐌': 148}, {'🐌': 174}, {'👎': 180}]

                activated = [False, False, False, False, [False, False, False]]

            elif lvl == '9':
                def check_lvl_conditions(cord: int, activated_: list):

                    cord, activated_[0] = double_door(141, 152, [118, 119], activated_[0], cord)
                    cord, activated_[1] = activator(91, 96, activated_[1], cord)
                    cord, activated_[2] = chooser(77, 128, 136, activated_[2], cord)
                    cord, activated_[3] = double_activator(16, 44, 50, activated_[3], cord)
                    cord, activated_[4] = activator(58, 71, activated_[4], cord, emoji=like_emoji_1)

                    return cord, activated_

                money_for_lvl = 90
                walls = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 51, 65, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 85,
                         86,
                         95, 115, 116, 117, 120, 121, 122, 124, 127, 130, 131, 134, 135, 138, 142, 143, 144, 149, 150,
                         151,
                         156, 157, 164, 165]

                player_model_condition = 174
                treasure_condition = 26
                bonus_condition = 129

                special_models = [{'⬜': 16}, {'🔒': 50}, {'🌳': 52}, {'🌹': 53}, {'🌻': 54}, {'🐌': 58},
                                  {'🌻': 66}, {'🌹': 67}, {'🌳': 68}, {'👎': 71}, {'🐇': 77}, {'🐌': 91},
                                  {dislike_emoji: 96},
                                  {'🟨': 118}, {'🟨': 119}, {'🍒': 128}, {'🥕': 136}, {'🔴': 141}, {'🔴': 152}]

                activated = [[False, False], False, [False, False, False], False, False]

            elif lvl == '10':
                def check_lvl_conditions(cord: int, activated_: list):

                    if not activated_[7]:

                        cord, activated_[0] = chooser(87, 17, 15, activated_[0], cord)
                        cord, activated_[1] = double_activator(22, 52, 113, activated_[1], cord)
                        cord, activated_[2] = activator(20, 68, activated_[2], cord)
                        cord, activated_[3] = double_door(19, 23, [104, 105], activated_[3], cord)
                        cord, activated_[4] = double_activator(155, 157, 124, activated_[4], cord, wall_emoji='🟪')
                        cord, activated_[5] = activator(178, 169, activated_[5], cord, like_emoji_1)
                        cord, activated_[6] = activator(179, 171, activated_[6], cord, like_emoji_1)
                        cord, activated_[7] = space_changer(switcher_cord=180,
                                                            new_player_condition=lvl_10_new_world_spawn,
                                                            treasure_cord=lvl_10_new_world_treasure,
                                                            new_space=lvl_10_new_world,
                                                            new_walls_conditions=lvl_10_new_world_walls,
                                                            player_condition=cord,
                                                            _activated=activated_[7])

                    elif activated_[7]:

                        cord, activated_[8] = chooser(127, 132, 17, activated_[8], cord)
                        cord, activated_[9] = activator(138, 24, activated_[9], cord)

                    return cord, activated_

                money_for_lvl = 100
                walls = [18, 24, 31, 32, 33, 34, 36, 37, 38, 45, 48, 59, 60, 61, 62, 66, 67, 73, 80, 82, 94, 101, 102,
                         103,
                         106, 107, 108, 109, 110, 115, 127, 128, 129, 132, 133, 134, 136, 137, 138, 146, 148, 150, 156,
                         158,
                         160, 161, 162, 164, 165, 166, 170, 172]
                player_model_condition = 85
                treasure_condition = 0
                bonus_condition = 26
                special_models = [{'🥕': 15}, {'🍒': 17}, {'🔴': 19}, {'🐌': 20}, {'⬜': 22}, {'🔴': 23}, {'🌴': 46},
                                  {'🌳': 47}, {'👎': 68}, {'🌳': 81}, {'🐇': 87}, {'🌹': 95}, {'🌻': 96}, {'🟨': 104},
                                  {'🟨': 105}, {'🔒': 113}, {'🔒': 124}, {'🌞': 147}, {'🌻': 151}, {'🌹': 152},
                                  {'🟪': 155},
                                  {'👎': 169}, {'👎': 171}, {'🐌': 178}, {'🐌': 179}, {'🖲': 180}]

                lvl_10_new_world_walls = [16, 25, 29, 30, 39, 40, 45, 46, 51, 52, 59, 60, 65, 66, 73, 74, 79, 80, 87,
                                          88, 93, 94, 128, 129, 136, 137, 143, 144, 145, 146, 147, 148, 149, 150]
                lvl_10_new_world_spawn = 99
                lvl_10_new_world_treasure = 174
                lvl_10_new_world_bonus = None
                lvl_10_new_world_special_models = [{'🌹': 15}, {'🥕': 17}, {'👎': 24}, {'🌹': 26}, {'🐇': 127},
                                                   {'🍒': 132}, {'🐌': 138}]

                lvl_10_new_world, lvl_10_new_world_walls = generate_space(
                    start_player_condition=lvl_10_new_world_spawn,
                    bonus_condition_=lvl_10_new_world_bonus,
                    treasure_condition_=lvl_10_new_world_treasure,
                    walls_=lvl_10_new_world_walls,
                    special_models_=lvl_10_new_world_special_models
                )

                activated = [[False, False, False], False, False, [False, False], False, False, False, False,
                             [False, False, False], False]

            space, walls_conditions = generate_space(player_model_condition, bonus_condition, treasure_condition, walls,
                                                     special_models)

            n_conditions = []
            n = 0

            for element in space:
                if element.endswith('\n'):
                    n_conditions.append(n)
                n += 1

            buttons = [[Button(style=ButtonStyle.gray, label=f'Help the {player_model} find a disk', disabled=True)],
                       [Button(style=ButtonStyle.blue, label='\u200b', disabled=True),
                        Button(style=ButtonStyle.blue, label='▲', custom_id='-14'),
                        Button(style=ButtonStyle.blue, label='\u200b', disabled=True)],
                       [Button(style=ButtonStyle.blue, label='◀', custom_id='-1'),
                        Button(style=ButtonStyle.blue, label='▼', custom_id='14'),
                        Button(style=ButtonStyle.blue, label='▶', custom_id='1')]]

            display_button = buttons[0][0]

            await message.edit(f"{ctx.author.mention}'s game \n" + ''.join(space), components=buttons)

            # Main cycle of the game
            while space[treasure_condition] != player_model:
                try:
                    inter = await self.bot.wait_for('button_click',
                                                    check=lambda i: i.author == ctx.message.author
                                                    and i.message == message, timeout=20)
                except asyncio.TimeoutError:
                    display_button.set_label('Time is up, the game is over')
                    display_button.set_style(ButtonStyle.red)

                    disable_buttons(buttons)

                    await message.edit(f"{ctx.author.mention}'s game \n" + ''.join(space), components=buttons)

                    break

                custom_id = int(inter.component.custom_id)
                old_player_condition = player_model_condition
                player_model_condition += custom_id

                try:
                    player_model_condition, activated = check_lvl_conditions(player_model_condition, activated)

                except StopIteration:
                    space[old_player_condition] = green_square
                    space[player_model_condition] = player_model

                    try:
                        disable_buttons(buttons)

                        await message.edit(f"{ctx.author.mention}'s game \n" + ''.join(space), components=buttons)
                        await inter.respond(type=6)

                    except discord.NotFound:

                        pass

                    break

                space[old_player_condition] = green_square

                if player_model_condition in walls_conditions:
                    if check_n_conditions():
                        player_model = '😳' + '\n'

                    else:
                        player_model = '😳'

                    space[player_model_condition] = player_model

                    display_button.set_label('🚫 You can not go on the wall')
                    display_button.set_style(ButtonStyle.red)

                    disable_buttons(buttons)

                    await message.edit(f"{ctx.author.mention}'s game \n" + ''.join(space), components=buttons)
                    await inter.respond(type=6)

                    break

                elif player_model_condition == bonus_condition:
                    bonus_collected = True

                space[player_model_condition] = player_model

                try:
                    asyncio.get_event_loop().create_task(message_edit())
                    asyncio.get_event_loop().create_task(interact_response())

                except discord.NotFound:
                    continue

            else:
                """
                When a player wins, he gets money, but if he collects a bonus disk, he gets 1.5 times more money.
                """

                if bonus_collected:
                    money_to_add = money_for_lvl * 1.5
                else:
                    money_to_add = money_for_lvl

                display_button.set_label(f'You helped the {player_model} find the disk and got {money_to_add} coins')
                display_button.set_style(ButtonStyle.green)
                disable_buttons(buttons)

                await message.edit(f"{ctx.author.mention}'s game \n" + ''.join(space), components=buttons)

                money += money_to_add

                if lvl_max < 10 and lvl == str(lvl_max):
                    lvl_max += 1

                self.sql.execute(f"UPDATE clown_db SET lvl = ?, money = ? WHERE user_id = ?",
                                 (lvl_max, money, ctx.message.author.id))
                self.db.commit()

            self.clown_online_list.remove(ctx.message.author.id)

        """----------------------------------------------------------------------------------------------------"""

        self.sql.execute(f"SELECT user_id FROM clown_db WHERE user_id = {ctx.message.author.id}")

        if self.sql.fetchone() is None:
            lvl_max = 1
            money = 0
            items_bought = ''
            item_equipped = '🤡'

            self.sql.execute(f"INSERT INTO clown_db VALUES (?, ?, ?, ?, ?)", (ctx.message.author.id, lvl_max, money,
                                                                              items_bought, item_equipped))
            self.db.commit()

        self.sql.execute(f"SELECT * FROM clown_db WHERE user_id = {ctx.message.author.id}")

        player_info = self.sql.fetchone()

        lvl_max = player_info[1]
        money = player_info[2]
        items_bought = player_info[3]
        item_equipped = player_info[4]

        await menu()


def setup(bot: commands.Bot):
    bot.add_cog(ClownGame(bot))
