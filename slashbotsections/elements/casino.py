# -*- coding: utf-8 -*-
import random
import discord
import reladdons

from typing import List, Dict
from discord.ext import commands
from datetime import datetime
from discord import app_commands

from database.db import Database
from botsections.functions.helperfunction import (
    fail_rand,
    get_color, divide_the_number, casino2ch, get_time, write_log
)
from botsections.functions.texts import *
from botsections.functions.config import settings

__all__ = (
    "CasinoSlash",
)


class CasinoSlash(commands.Cog):
    NAME = 'Casino module'

    __slots__ = (
        "db", "bot", "result_bid", "casino", "rust_casino",
        "color", "dropped_coefficient", "line1", "line2",
        "line3", "texts", "count", "emb", "num"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.bot: commands.Bot = bot
        self.color: discord.Color
        self.emb: discord.Embed
        self.casino: Dict[int, Dict[str, list]] = {}
        self.line1: List[int] = []
        self.line2: List[int] = []
        self.line3: List[int] = []
        self.rust_casino: List[int] = casino_rust.copy()
        self.texts: dict = {}
        self.dropped_coefficient: float
        self.casino_num: int = 0
        self.count: int = 0
        self.num: int = 0
        self.result_bid: int
        self.date_now: datetime
        print(f"[{get_time()}] [INFO]: Casino connected")
        write_log(f"[{get_time()}] [INFO]: Casino connected")

    @app_commands.command(name="wheel")
    @app_commands.guilds(493970394374471680)
    async def __casino_3(
            self, inter: discord.Interaction,
            bid: int = None, number: int = None
    ) -> None:
        if self.db.is_the_casino_allowed(inter.message.channel.id):
            if bid is None:
                await inter.response.send_message("Вы ну ввели Вашу ставку!", ephemeral=True)
            elif bid <= 0:
                await inter.response.send_message("Вы не можете поставить ставку, которая меньше 1!", ephemeral=True)
            elif self.db.get_cash(inter.user.id, inter.guild.id) < bid:
                await inter.response.send_message("У Вас не достаточно денег для этой ставки!", ephemeral=True)
            else:
                if number is None:
                    await inter.response.send_message(
                        "Вы не ввели число! (Либо 1, либо 3, либо 5, либо 10, либо 20)",
                        ephemeral=True
                    )
                else:
                    self.color = get_color(inter.user.roles)
                    random.shuffle(self.rust_casino)
                    print(self.rust_casino)
                    if number in [1, 3, 5, 10, 20]:
                        self.db.take_coins(inter.user.id, inter.guild.id, bid)

                        if self.rust_casino[0] == number:
                            self.db.add_coins(inter.user.id, inter.guild.id, (self.rust_casino[0] * bid))
                            self.emb = discord.Embed(
                                title="🎰Вы выиграли!🎰",
                                colour=self.color
                            )
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value=f'{inter.user.mention}, '
                                      f'Вы выиграли **{divide_the_number(self.rust_casino[0] * bid)}** '
                                      f'DP коинов!',
                                inline=False
                            )
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RustCasinosCount", "RustCasino", "WinsCount", bid)
                        elif self.rust_casino[0] != number:
                            self.emb = discord.Embed(
                                title="🎰Вы проиграли!🎰",
                                colour=self.color
                            )
                            self.emb.add_field(
                                name=f'Вы проиграли:(',
                                value=f'{inter.user.mention}, выпало число {self.rust_casino[0]}',
                                inline=False
                            )
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RustCasinosCount", "RustCasino", "LosesCount", -bid)
                    else:
                        await inter.response.send_message(
                            f"Вы должны поставить либо 1, либо 3, либо 5, либо 10, либо 20!",
                            ephemeral=True
                        )
        else:
            await inter.response.send_message(
                f"Вы можете играть в казино только в специальном канале!", ephemeral=True
            )

    @app_commands.command(name="fail")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __fail(
            self, inter: discord.Interaction,
            bid: int = None, coefficient: float = None
    ) -> None:
        if self.db.is_the_casino_allowed(inter.message.channel.id):
            if bid is None:
                await inter.response.send_message(f"Вы не ввели вашу ставку", ephemeral=True)
            elif bid < 10:
                await inter.response.send_message(f"Вы не можете поставить ставку меньше 10", ephemeral=True)
            elif coefficient is None:
                await inter.response.send_message(f"Вы не ввели коэффициент", ephemeral=True)
            elif coefficient < 0.07:
                await inter.response.send_message(f"Вы не можете поставить на коэффициент ниже 0.07", ephemeral=True)
            elif coefficient > 10:
                await inter.response.send_message(f"Вы не можете поставить на коэффициент больше 10", ephemeral=True)
            elif self.db.get_cash(inter.user.id, inter.guild.id) < bid:
                await inter.response.send_message(f"У Вас недостаточно средств", ephemeral=True)
            else:
                self.db.take_coins(inter.user.id, inter.guild.id, bid)
                self.dropped_coefficient = fail_rand(inter.user.id)[0]
                self.color = get_color(inter.user.roles)
                if self.dropped_coefficient < coefficient:
                    self.emb = discord.Embed(
                        title="🎰Вы проиграли!🎰" +
                              [" Вам выпал 0.00...🎰" if self.dropped_coefficient == 0 else ""][0],
                        colour=self.color
                    )
                    self.emb.add_field(
                        name=f':(',
                        value=f'Выпало число `{self.dropped_coefficient}`\n{inter.user}',
                        inline=False
                    )
                    await inter.response.send_message(embed=self.emb)
                    if self.dropped_coefficient == 0:
                        if not self.db.check_completion_dropping_zero_in_fail_achievement(inter.user.id,
                                                                                          inter.guild.id):
                            self.db.add_coins(inter.user.id, inter.guild.id, 4000)
                            self.db.complete_dropping_zero_in_fail_achievement(inter.user.id, inter.guild.id)
                            try:
                                await inter.user.response.send_message(
                                    "Поздравляем, Вы забрали сумму которую поставили. А, нет, не забрали, "
                                    "разработчик до сих пор не пофиксил это...\nНу или пофиксил..."
                                    "\nВот тебе скромная награда! (4000 коинов)"
                                )
                            except discord.errors.Forbidden:
                                pass
                    await self.db.stats_update(inter, "FailsCount", "Fails", "LosesCount", -bid)
                else:
                    self.db.add_coins(inter.user.id, inter.guild.id, bid + int(bid * coefficient))
                    self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                    self.emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value=f'Выпало число `{self.dropped_coefficient}`\n{inter.user}, Вы выиграли '
                              f'**{divide_the_number(bid + int(bid * coefficient))}** DP коинов!',
                        inline=False
                    )
                    await inter.response.send_message(embed=self.emb)
                    await self.db.stats_update(inter, "FailsCount", "Fails", "WinsCount", bid + int(bid * coefficient))
        else:
            await inter.response.send_message(f"Вы можете играть в казино только в специальном канале!", ephemeral=True)

    @app_commands.command(name="777")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino777(self, inter: discord.Interaction, bid: int) -> None:
        if inter.user.id != 0:
            return
        if self.db.is_the_casino_allowed(inter.message.channel.id):
            if bid is None:
                await inter.response.send_message(f"Вы не ввели вашу ставку", ephemeral=True)
            elif bid < 10:
                await inter.response.send_message(f"Вы не можете поставить ставку меньше 10", ephemeral=True)
            else:
                self.color = get_color(inter.user.roles)
                self.result_bid = bid
                self.db.take_coins(inter.user.id, inter.guild.id, bid)
                self.line1 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=7,
                    array_long=5,
                    key=str(inter.user.id)
                )
                self.line2 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3, shuffle_long=9,
                    array_long=5,
                    key=str(inter.user.id)
                )
                self.line3 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=8,
                    array_long=5,
                    key=str(inter.user.id)
                )
                if self.line2[1] == "8":
                    self.result_bid *= 2
                elif self.line2[1] == "0":
                    self.result_bid *= 3
                elif self.line2[1] == "7":
                    self.result_bid *= 5
                elif self.line2[1] == "1":
                    self.result_bid *= 1
                if self.line2[0] == self.line2[1] and self.line2[1] == self.line2[2]:
                    self.db.add_coins(inter.user.id, inter.guild.id, self.result_bid)
                    self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                    self.emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *self.line1[0], *self.line1[1], *self.line1[2],
                            *self.line2[0], *self.line2[1], *self.line2[2],
                            *self.line3[0], *self.line3[1], *self.line3[2],
                            inter.user.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await inter.response.send_message(embed=self.emb)
                    await self.db.stats_update(inter, "ThreeSevensCount", "ThreeSevens", "WinsCount", self.result_bid)

                elif self.line1[2] == self.line2[1] and self.line2[1] == self.line3[0]:
                    self.db.add_coins(inter.user.id, inter.guild.id, self.result_bid)
                    self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                    self.emb.add_field(
                        name=f'🎰Вы выиграли!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *self.line1[0], *self.line1[1], *self.line1[2],
                            *self.line2[0], *self.line2[1], *self.line2[2],
                            *self.line3[0], *self.line3[1], *self.line3[2],
                            inter.user.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    self.db.add_coins(inter.user.id, inter.guild.id, self.result_bid)
                    await inter.response.send_message(embed=self.emb)
                    await self.db.stats_update(inter, "ThreeSevensCount", "ThreeSevens", "WinsCount", self.result_bid)

                else:
                    self.emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=self.color)
                    self.emb.add_field(
                        name=f':(',
                        value='{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *self.line1[0], *self.line1[1], *self.line1[2],
                            *self.line2[0], *self.line2[1], *self.line2[2],
                            *self.line3[0], *self.line3[1], *self.line3[2],
                            inter.user.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await inter.response.send_message(embed=self.emb)
                    await self.db.stats_update(inter, "ThreeSevensCount", "ThreeSevens", "LosesCount", -bid)

        else:
            await inter.response.send_message(f"Вы можете играть в казино только в специальном канале!", ephemeral=True)

    @app_commands.command(name="coinflip")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_2(self, inter: discord.Interaction, count: int, member: discord.Member = None):
        self.date_now = get_time()
        self.color = get_color(inter.user.roles)
        if self.db.is_the_casino_allowed(inter.message.channel.id):
            if member is None:
                if await self.db.cash_check(inter, count, min_cash=10, check=True):
                    self.db.take_coins(inter.user.id, inter.guild.id, count)
                    self.casino_num = casino2ch(inter.user.id)[0]
                    if self.casino_num == 1:
                        self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                        self.emb.add_field(
                            name=f'Поздравляем!',
                            value=f'{inter.user.mention}, Вы выиграли **{divide_the_number(count * 2)}** DP коинов!',
                            inline=False
                        )
                        await inter.response.send_message(embed=self.emb)
                        self.db.add_coins(inter.user.id, inter.guild.id, count * 2)
                        await self.db.stats_update(inter, "CoinFlipsCount", "CoinFlips", "WinsCount", count * 2)

                    else:
                        self.emb = discord.Embed(title="Вы проиграли:(", colour=self.color)
                        self.emb.add_field(
                            name=f'Вы проиграли:(',
                            value=f'{inter.user.mention}, значит в следующий раз',
                            inline=False
                        )
                        await inter.response.send_message(embed=self.emb)
                        await self.db.stats_update(inter, "CoinFlipsCount", "CoinFlips", "LosesCount", -count)

            elif member is not None:
                if count <= 9:
                    await inter.response.send_message(f"Вы не можете поставить ставку меньше 10", ephemeral=True)
                elif inter.user.id == member.id:
                    await inter.response.send_message("Вы не можете играть с самим собой", ephemeral=True)
                elif count is None:
                    await inter.response.send_message(f"Вы не ввели вашу ставку", ephemeral=True)
                elif self.db.get_cash(inter.user.id, inter.guild.id) < count:
                    await inter.response.send_message(f"У Вас недостаточно средств", ephemeral=True)
                elif self.db.get_cash(member.id, inter.guild.id) < count:
                    await inter.response.send_message(f"У Вашего оппонента недостаточно средств", ephemeral=True)
                else:
                    if self.db.get_active_coinflip(inter.user.id, member.id, inter.guild.id):
                        await inter.response.send_message(
                            f"{inter.user.mention}, такая игра уже существует! Для удаления - "
                            f"{settings['prefix']}del_games "
                            f"{member.mention}"
                        )
                    else:
                        self.db.insert_into_coinflip(
                            inter.user.id, member.id,
                            str(inter.user), str(member),
                            inter.guild.id, str(inter.guild),
                            count, str(self.date_now)
                        )
                        self.emb = discord.Embed(title=f"{member}, вас упомянули в коинфлипе!", colour=self.color)
                        self.emb.add_field(
                            name=f'Коинфлип на {count} DP коинов!',
                            value=f"{inter.user.mention}, значит в следующий раз"
                                  f"{settings['prefix']}accept {inter.user.mention}\n\nЧтобы отменить - "
                                  f"{settings['prefix']}reject {inter.user.mention}",
                            inline=False
                        )
                        await inter.response.send_message(embed=self.emb)
                        await inter.response.send_message(member.mention)
        else:
            await inter.response.send_message(f"Вы можете играть в казино только в специальном канале!", ephemeral=True)

    @app_commands.command(name="roll")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __roll(self, inter: discord.Interaction, count: int = None, *args):
        self.color = get_color(inter.user.roles)
        self.count = count
        if self.db.is_the_casino_allowed(inter.message.channel.id):
            if await self.db.cash_check(inter, self.count, min_cash=10, check=True):
                self.texts[inter.user.id] = ""
                self.casino[inter.user.id] = {}
                self.casino[inter.user.id]["color"] = reladdons.randoms.choice(
                    "black", "red", shuffle_long=37, key=str(inter.user.id), array_long=37
                )
                self.casino[inter.user.id]["number"] = reladdons.randoms.randint(
                    0, 36, key=str(inter.user.id), shuffle_long=37, array_long=37
                )
                # casino2[inter.user.id]["number"] = 1, [random.randint(0, 36), random.randint(0, 36)]
                for i in args:
                    self.texts[inter.user.id] += i
                try:
                    self.casino[inter.user.id]["color"][0] = casino_numbers_color[
                        self.casino[inter.user.id]["number"][0]
                    ]
                    if int(self.texts[inter.user.id][0]) < 0:
                        pass
                    elif int(self.texts[inter.user.id][0]) > 36:
                        pass
                    else:
                        self.db.take_coins(inter.user.id, inter.guild.id, self.count)
                        if int(self.texts[inter.user.id]) == 0 and int(self.texts[inter.user.id][0]) \
                                == self.casino[inter.user.id]["number"][0]:
                            self.count *= 35
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value='Выпало число {}, green\n{}'
                                      ", Вы выиграли **{}** DP коинов!!".format(
                                        self.casino[inter.user.id]['number'][0],
                                        inter.user.mention,
                                        divide_the_number(self.count)
                                        ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif int(self.texts[inter.user.id]) == self.casino[inter.user.id]["number"][0]:
                            self.count *= 35
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)
                        else:
                            self.emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы  проиграли:(".format(
                                        self.casino[inter.user.id]['number'][0],
                                        self.casino[inter.user.id]['color'][0],
                                        inter.user.mention
                                        ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            self.count = -self.count
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "LosesCount", self.count)
                except ValueError:
                    if self.texts[inter.user.id] in roll_types:
                        self.db.take_coins(inter.user.id, inter.guild.id, self.count)
                        if self.texts[inter.user.id] == "1st12" and self.casino[inter.user.id]["number"][0] <= 12:
                            self.count *= 3
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "2nd12" and \
                                24 >= self.casino[inter.user.id]["number"][0] > 12:
                            self.count *= 3
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "3rd12" and self.casino[inter.user.id]["number"][0] > 24:
                            self.count *= 3
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "1to18" and \
                                0 != self.casino[inter.user.id]["number"][0] <= 18:
                            self.count *= 2
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "19to36" and \
                                18 < self.casino[inter.user.id]["number"][0] <= 36:
                            self.count *= 2
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "2to1" and self.casino[inter.user.id]["number"][0] in row1:
                            self.count *= 3
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "2to2" and self.casino[inter.user.id]["number"][0] in row2:
                            self.count *= 3
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "2to3" and self.casino[inter.user.id]["number"][0] in row3:
                            self.count *= 3
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "b" and self.casino[inter.user.id]["color"][0] == "black":
                            self.count *= 2
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)

                        elif self.texts[inter.user.id] == "r" and self.casino[inter.user.id]["color"][0] == "red":
                            self.count *= 2
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)
                        elif self.texts[inter.user.id] == "ch" and self.casino[inter.user.id]["number"][0] % 2 == 0:
                            self.count *= 2
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)
                        elif self.texts[inter.user.id] == "nch" and self.casino[inter.user.id]["number"][0] % 2 == 1:
                            self.count *= 2
                            self.db.add_coins(inter.user.id, inter.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[inter.user.id]["number"][0],
                                    self.casino[inter.user.id]["color"][0],
                                    inter.user.mention, divide_the_number(self.count)
                                ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", self.count)
                        else:
                            self.emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы проиграли:(".format(
                                        self.casino[inter.user.id]['number'][0],
                                        self.casino[inter.user.id]['color'][0],
                                        inter.user.mention
                                        ),
                                inline=False)
                            await inter.response.send_message(embed=self.emb)
                            await self.db.stats_update(inter, "RollsCount", "Rolls", "WinsCount", -self.count)

                    else:
                        await inter.response.send_message(f"Такого атрибута не существует! ", ephemeral=True)
        else:
            await inter.response.send_message(f"Вы можете играть в казино только в специальном канале!", ephemeral=True)

    @app_commands.command(name="del_games")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __del_games(self, inter: discord.Interaction, member: discord.Member = None):
        if member is None:
            self.db.delete_from_coinflip(inter.user.id, inter.guild.id, inter.guild.id)
            await inter.message.add_reaction('✅')
        else:
            if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
                self.db.delete_from_coinflip(member.id, member.id, inter.guild.id)
                await inter.message.add_reaction('✅')
            else:
                await inter.response.send_message("Ты чё ку-ку? Тебе так нельзя.", ephemeral=True)

    @app_commands.command(name="reject")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __reject(self, inter: discord.Interaction, member: discord.Member):
        if member is None:
            await inter.response.send_message("Вы не указали человека", ephemeral=True)
        elif member.id == inter.user.id:
            await inter.response.send_message("Вы не можете указать себя", ephemeral=True)
        elif not self.db.get_active_coinflip(inter.user.id, member.id, inter.guild.id):
            await inter.response.send_message(
                f"Такой игры не существует, посмотреть все ваши активные игры - {settings['prefix']}games",
                ephemeral=True
            )
        else:
            self.db.delete_from_coinflip(inter.user.id, member.id, inter.guild.id)
            await inter.message.add_reaction('✅')

    @app_commands.command(name="games")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __games(self, inter: discord.Interaction):
        if not self.db.check_coinflip_games(inter.user.id, inter.guild.id):
            self.emb = discord.Embed(title="Активные коинфлипы")
            for row in self.db.get_player_active_coinflip(inter.user.id, inter.guild.id):
                self.emb.add_field(
                    name=f'{inter.user} и {row[0]}',
                    value=f'Сумма: {row[1]}',
                    inline=False
                )
            for row in self.db.get_player_active_coinflip(inter.user.id, inter.guild.id, True):
                self.emb.add_field(
                    name=f'**{row[0]}** и **{inter.user}**',
                    value=f'Сумма: **{row[1]}**',
                    inline=False
                )
            await inter.response.send_message(embed=self.emb)
        else:
            await inter.response.send_message("У Вас нет активных игр", ephemeral=True)

    @app_commands.command(name="accept")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __c_accept(self, inter: discord.Interaction, member: discord.Member):
        if member is None:
            await inter.response.send_message("Вы не указали человека", ephemeral=True)
        elif not self.db.get_active_coinflip(inter.user.id, member.id, inter.guild.id):
            await inter.response.send_message(
                f"Такой игры не существует, посмотреть все ваши активные игры - {settings['prefix']}games",
                ephemeral=True
            )
        elif reladdons.long.minutes(self.db.get_from_coinflip(inter.user.id, member.id, inter.guild.id, "Date")) > 5:
            await inter.response.send_message(f"Время истекло:(", ephemeral=True)
            self.db.delete_from_coinflip(inter.user.id, member.id, inter.guild.id)
        elif self.db.get_cash(inter.user.id, inter.guild.id) < \
                self.db.get_from_coinflip(inter.user.id, member.id, inter.guild.id, "Cash"):
            await inter.response.send_message(f"У Вас недостаточно средств!", ephemeral=True)
        elif self.db.get_cash(member.id, inter.guild.id) < \
                self.db.get_from_coinflip(inter.user.id, member.id, inter.guild.id, "Cash"):
            await inter.response.send_message(f"У Вашего cоперника недостаточно средств", ephemeral=True)
        else:
            self.num = self.db.get_from_coinflip(inter.user.id, member.id, inter.guild.id, "Cash")
            self.db.take_coins(inter.user.id, inter.guild.id, self.num)
            self.db.take_coins(member.id, inter.guild.id, self.num)
            self.ch = random.randint(1, 2)
            # if member.id == 401555829620211723:
            #       self.ch = 2
            if self.ch == 1:
                self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(inter.user.roles))
                self.emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{inter.user.mention}, Вы выиграли **{divide_the_number(self.num * 2)}** DP коинов!',
                    inline=False
                )
                await inter.response.send_message(embed=self.emb)
                self.db.add_coins(inter.user.id, inter.guild.id, self.num * 2)
                self.db.add_lose(member.id, inter.guild.id)
                self.db.add_win(member.id, inter.guild.id, null=True)
                self.db.add_win(inter.user.id, inter.guild.id)
                self.db.add_lose(inter.user.id, inter.guild.id, null=True)
                await self.db.achievement_member(member)
                await self.db.achievement(inter)
                await self.db.stats_update(inter, "CoinFlipsCount", "CoinFlips", "WinsCount", self.num * 2)
                self.db.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "LosesCount", self.num * 2
                )
            else:
                self.db.add_lose(inter.user.id, inter.guild.id)
                self.db.add_win(inter.user.id, inter.guild.id, null=True)
                self.db.add_win(member.id, inter.guild.id)
                self.db.add_lose(member.id, inter.guild.id, null=True)
                await self.db.achievement_member(member)
                await self.db.achievement(inter)
                self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(inter.user.roles))
                self.emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{member.mention}, Вы выиграли **{divide_the_number(self.num * 2)}** DP коинов!',
                    inline=False
                )
                await inter.response.send_message(embed=self.emb)
                self.db.add_coins(member.id, member.guild.id, self.num * 2)
                self.db.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "WinsCount", self.num * 2
                )
                await self.db.stats_update(inter, "CoinFlipsCount", "CoinFlips", "LosesCount", self.num * 2)
            self.db.delete_from_coinflip(inter.user.id, member.id, inter.guild.id)
