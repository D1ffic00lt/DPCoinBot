# -*- coding: utf-8 -*-
import random
import discord
import reladdons

from typing import List, Union
from discord.ext import commands
from datetime import datetime

from database.db import Database
from botsections.functions.helperfunction import (
    fail_rand,
    get_color, divide_the_number, casino2ch, get_time, write_log
)
from botsections.functions.texts import *
from botsections.functions.config import settings

__all__ = (
    "Casino",
)


class Casino(commands.Cog):
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
        self.casino: List[Union[list, dict]] = []
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

    @commands.command(aliases=['rust_casino'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_3(
            self, ctx: commands.context.Context,
            bid: int = None, number: int = None
    ) -> None:
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.send("Вы ну ввели Вашу ставку!")
            elif bid <= 0:
                await ctx.send("Вы не можете поставить ставку, которая меньше 1!")
            elif self.db.get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.send("У Вас не достаточно денег для этой ставки!")
            else:
                if number is None:
                    await ctx.send("Вы не ввели число! (Либо 1, либо 3, либо 5, либо 10, либо 20)")
                else:
                    self.color = get_color(ctx.author.roles)
                    random.shuffle(self.rust_casino)
                    print(self.rust_casino)
                    if number in [1, 3, 5, 10, 20]:
                        self.db.take_coins(ctx.author.id, ctx.guild.id, bid)

                        if self.rust_casino[0] == number:
                            self.db.add_coins(ctx.author.id, ctx.guild.id, (self.rust_casino[0] * bid))
                            self.emb = discord.Embed(
                                title="🎰Вы выиграли!🎰",
                                colour=self.color
                            )
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value=f'{ctx.author.mention}, '
                                      f'Вы выиграли **{divide_the_number(self.rust_casino[0] * bid)}** '
                                      f'DP коинов!',
                                inline=False
                            )
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RustCasinosCount", "RustCasino", "WinsCount", bid)
                        elif self.rust_casino[0] != number:
                            self.emb = discord.Embed(
                                title="🎰Вы проиграли!🎰",
                                colour=self.color
                            )
                            self.emb.add_field(
                                name=f'Вы проиграли:(',
                                value=f'{ctx.author.mention}, выпало число {self.rust_casino[0]}',
                                inline=False
                            )
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RustCasinosCount", "RustCasino", "LosesCount", -bid)
                    else:
                        await ctx.send(
                            f"{ctx.author.mention}, Вы должны поставить либо 1, либо 3, либо 5, либо 10, либо 20!"
                        )
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!"
                           )

    @commands.command(aliases=['fail'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __fail(
            self, ctx: commands.context.Context,
            bid: int = None, coefficient: float = None
    ) -> None:
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.send(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.send(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            elif coefficient is None:
                await ctx.send(f"{ctx.author.mention}, Вы не ввели коэффициент")
            elif coefficient < 0.04:
                await ctx.send(f"{ctx.author.mention}, Вы не можете поставить на коэффициент ниже 0.04")
            elif coefficient > 10:
                await ctx.send(f"{ctx.author.mention}, Вы не можете поставить на коэффициент больше 10")
            elif self.db.get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.send(f"{ctx.author.mention}, У Вас недостаточно средств")
            else:
                self.db.take_coins(ctx.author.id, ctx.guild.id, bid)
                self.dropped_coefficient = fail_rand(ctx.author.id)[0]
                self.color = get_color(ctx.author.roles)
                if self.dropped_coefficient > coefficient:
                    self.emb = discord.Embed(
                        title="🎰Вы проиграли!🎰" +
                              [" Вам выпал 0.00...🎰" if self.dropped_coefficient == 0 else ""][0],
                        colour=self.color
                    )
                    self.emb.add_field(
                        name=f':(',
                        value=f'Выпало число `{self.dropped_coefficient}`\n{ctx.author}',
                        inline=False
                    )
                    await ctx.send(embed=self.emb)
                    if self.dropped_coefficient == 0:
                        if not self.db.check_completion_dropping_zero_in_fail_achievement(ctx.author.id, ctx.guild.id):
                            self.db.add_coins(ctx.author.id, ctx.guild.id, 4000)
                            self.db.complete_dropping_zero_in_fail_achievement(ctx.author.id, ctx.guild.id)
                            try:
                                await ctx.author.send(
                                    "Поздравляем, Вы забрали сумму которую поставили. А, нет, не забрали, "
                                    "разработчик до сих пор не пофиксил это...\nНу или пофиксил..."
                                    "\nВот тебе скромная награда! (4000 коинов)"
                                )
                            except discord.errors.Forbidden:
                                pass
                    await self.db.stats_update(ctx, "FailsCount", "Fails", "LosesCount", -bid)
                else:
                    self.db.add_coins(ctx.author.id, ctx.guild.id, int(bid * coefficient))
                    self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                    self.emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value=f'Выпало число `{self.dropped_coefficient}`\n{ctx.author}, Вы выиграли '
                              f'**{divide_the_number(int(bid * coefficient))}** DP коинов!',
                        inline=False
                    )
                    await ctx.send(embed=self.emb)
                    await self.db.stats_update(ctx, "FailsCount", "Fails", "WinsCount", int(bid * coefficient))
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['777'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __casino777(self, ctx: commands.context.Context, bid: int = None) -> None:
        if ctx.author.id != 0:
            return
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.send(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.send(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            else:
                self.color = get_color(ctx.author.roles)
                self.result_bid = bid
                self.db.take_coins(ctx.author.id, ctx.guild.id, bid)
                self.line1 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=7,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                self.line2 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3, shuffle_long=9,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                self.line3 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=8,
                    array_long=5,
                    key=str(ctx.author.id)
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
                    self.db.add_coins(ctx.author.id, ctx.guild.id, self.result_bid)
                    self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                    self.emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *self.line1[0], *self.line1[1], *self.line1[2],
                            *self.line2[0], *self.line2[1], *self.line2[2],
                            *self.line3[0], *self.line3[1], *self.line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await ctx.send(embed=self.emb)
                    await self.db.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "WinsCount", self.result_bid)

                elif self.line1[2] == self.line2[1] and self.line2[1] == self.line3[0]:
                    self.db.add_coins(ctx.author.id, ctx.guild.id, self.result_bid)
                    self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                    self.emb.add_field(
                        name=f'🎰Вы выиграли!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *self.line1[0], *self.line1[1], *self.line1[2],
                            *self.line2[0], *self.line2[1], *self.line2[2],
                            *self.line3[0], *self.line3[1], *self.line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    self.db.add_coins(ctx.author.id, ctx.guild.id, self.result_bid)
                    await ctx.send(embed=self.emb)
                    await self.db.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "WinsCount", self.result_bid)

                else:
                    self.emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=self.color)
                    self.emb.add_field(
                        name=f':(',
                        value='{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *self.line1[0], *self.line1[1], *self.line1[2],
                            *self.line2[0], *self.line2[1], *self.line2[2],
                            *self.line3[0], *self.line3[1], *self.line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await ctx.send(embed=self.emb)
                    await self.db.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "LosesCount", -bid)

        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['coinflip'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def __casino_2(self, ctx: commands.context.Context, count: int = None, member: discord.Member = None):
        self.date_now = get_time()
        self.color = get_color(ctx.author.roles)
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if member is None:
                if await self.db.cash_check(ctx, count, min_cash=10, check=True):
                    self.db.take_coins(ctx.author.id, ctx.guild.id, count)
                    self.casino_num = casino2ch(ctx.author.id)[0]
                    if self.casino_num == 1:
                        self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                        self.emb.add_field(
                            name=f'Поздравляем!',
                            value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(count * 2)}** DP коинов!',
                            inline=False
                        )
                        await ctx.send(embed=self.emb)
                        self.db.add_coins(ctx.author.id, ctx.guild.id, count * 2)
                        await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "WinsCount", count * 2)

                    else:
                        self.emb = discord.Embed(title="Вы проиграли:(", colour=self.color)
                        self.emb.add_field(
                            name=f'Вы проиграли:(',
                            value=f'{ctx.author.mention}, значит в следующий раз',
                            inline=False
                        )
                        await ctx.send(embed=self.emb)
                        await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "LosesCount", -count)

            elif member is not None:
                if count <= 9:
                    await ctx.send(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
                elif ctx.author.id == member.id:
                    await ctx.send("Вы не можете играть с самим собой")
                elif count is None:
                    await ctx.send(f"{ctx.author.mention}, Вы не ввели вашу ставку")
                elif self.db.get_cash(ctx.author.id, ctx.guild.id) < count:
                    await ctx.send(f"{ctx.author.mention}, У Вас недостаточно средств")
                elif self.db.get_cash(member.id, ctx.guild.id) < count:
                    await ctx.send(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
                else:
                    if self.db.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
                        await ctx.send(
                            f"{ctx.author.mention}, такая игра уже существует! Для удаления - "
                            f"{settings['prefix']}del_games "
                            f"{member.mention}"
                        )
                    else:
                        self.db.insert_into_coinflip(
                            ctx.author.id, member.id,
                            str(ctx.author), str(member),
                            ctx.guild.id, str(ctx.guild),
                            count, str(self.date_now)
                        )
                        self.emb = discord.Embed(title=f"{member}, вас упомянули в коинфлипе!", colour=self.color)
                        self.emb.add_field(
                            name=f'Коинфлип на {count} DP коинов!',
                            value=f"{ctx.author.mention}, значит в следующий раз"
                                  f"{settings['prefix']}accept {ctx.author.mention}\n\nЧтобы отменить - "
                                  f"{settings['prefix']}reject {ctx.author.mention}",
                            inline=False
                        )
                        await ctx.send(embed=self.emb)
                        await ctx.send(member.mention)
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=["roll"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __roll(self, ctx: commands.context.Context, count: int = None, *args):
        self.color = get_color(ctx.author.roles)
        self.count = count
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if await self.db.cash_check(ctx, self.count, min_cash=10, check=True):
                self.texts[ctx.author.id] = ""
                self.casino[ctx.author.id] = {}
                self.casino[ctx.author.id]["color"] = reladdons.randoms.choice(
                    "black", "red", shuffle_long=37, key=str(ctx.author.id), array_long=37
                )
                self.casino[ctx.author.id]["number"] = reladdons.randoms.randint(
                    0, 36, key=str(ctx.author.id), shuffle_long=37, array_long=37
                )
                # casino2[ctx.author.id]["number"] = 1, [random.randint(0, 36), random.randint(0, 36)]
                for i in args:
                    self.texts[ctx.author.id] += i
                try:
                    self.casino[ctx.author.id]["color"][0] = casino_numbers_color[
                        self.casino[ctx.author.id]["number"][0]
                    ]
                    if int(self.texts[ctx.author.id][0]) < 0:
                        pass
                    elif int(self.texts[ctx.author.id][0]) > 36:
                        pass
                    else:
                        self.db.take_coins(ctx.author.id, ctx.guild.id, self.count)
                        if int(self.texts[ctx.author.id]) == 0 and int(self.texts[ctx.author.id][0]) \
                                == self.casino[ctx.author.id]["number"][0]:
                            self.count *= 35
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value='Выпало число {}, green\n{}'
                                      ", Вы выиграли **{}** DP коинов!!".format(
                                    self.casino[ctx.author.id]['number'][0],
                                    ctx.author.mention,
                                    divide_the_number(self.count)
                                ),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif int(self.texts[ctx.author.id]) == self.casino[ctx.author.id]["number"][0]:
                            self.count *= 35
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)
                        else:
                            self.emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы  проиграли:(".format(self.casino[ctx.author.id]['number'][0],
                                                                     *self.casino[ctx.author.id]['color'],
                                                                     ctx.author.mention),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            self.count = -self.count
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "LosesCount", self.count)
                except ValueError:
                    if self.texts[ctx.author.id] in roll_types:
                        self.db.take_coins(ctx.author.id, ctx.guild.id, self.count)
                        if self.texts[ctx.author.id] == "1st12" and self.casino[ctx.author.id]["number"][0] <= 12:
                            self.count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "2nd12" and \
                                24 >= self.casino[ctx.author.id]["number"][0] > 12:
                            self.count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "3rd12" and self.casino[ctx.author.id]["number"][0] > 24:
                            self.count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "1to18" and \
                                0 != self.casino[ctx.author.id]["number"][0] <= 18:
                            self.count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "19to36" and \
                                18 < self.casino[ctx.author.id]["number"][0] <= 36:
                            self.count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "2to1" and self.casino[ctx.author.id]["number"][0] in row1:
                            self.count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "2to2" and self.casino[ctx.author.id]["number"][0] in row2:
                            self.count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "2to3" and self.casino[ctx.author.id]["number"][0] in row3:
                            self.count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "b" and self.casino[ctx.author.id]["color"][0] == "black":
                            self.count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)

                        elif self.texts[ctx.author.id] == "r" and self.casino[ctx.author.id]["color"][0] == "red":
                            self.count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)
                        elif self.texts[ctx.author.id] == "ch" and self.casino[ctx.author.id]["number"][0] % 2 == 0:
                            self.count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)
                        elif self.texts[ctx.author.id] == "nch" and self.casino[ctx.author.id]["number"][0] % 2 == 1:
                            self.count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, self.count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(self.count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", self.count)
                        else:
                            self.emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы проиграли:(".format(self.casino[ctx.author.id]['number'][0],
                                                                    *self.casino[ctx.author.id]['color'],
                                                                    ctx.author.mention),
                                inline=False)
                            await ctx.send(embed=self.emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", -self.count)

                    else:
                        await ctx.send(f"{ctx.author.mention}, Такого атрибута не существует! ")
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['del_games'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __del_games(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            self.db.delete_from_coinflip(ctx.author.id, ctx.guild.id, ctx.guild.id)
            await ctx.message.add_reaction('✅')
        else:
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                self.db.delete_from_coinflip(member.id, member.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
            else:
                await ctx.send("Ты чё ку-ку? Тебе так нельзя.")

    @commands.command(aliases=['reject'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __reject(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            await ctx.send("Вы не ввели человека")
        elif member.id == ctx.author.id:
            await ctx.send("Вы не можете ввести себя")
        elif not self.db.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
            await ctx.send(f"Такой игры не существует, посмотреть все ваши активные игры - "
                           f"{settings['prefix']}games")
        else:
            self.db.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['games'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def __games(self, ctx: commands.context.Context):
        if not self.db.check_coinflip_games(ctx.author.id, ctx.guild.id):
            self.emb = discord.Embed(title="Активные коинфлипы")
            for row in self.db.get_player_active_coinflip(ctx.author.id, ctx.guild.id):
                self.emb.add_field(
                    name=f'{ctx.author} и {row[0]}',
                    value=f'Сумма: {row[1]}',
                    inline=False
                )
            for row in self.db.get_player_active_coinflip(ctx.author.id, ctx.guild.id, True):
                self.emb.add_field(
                    name=f'**{row[0]}** и **{ctx.author}**',
                    value=f'Сумма: **{row[1]}**',
                    inline=False
                )
            await ctx.send(embed=self.emb)
        else:
            await ctx.send("У Вас нет активных игр")

    @commands.command(aliases=['accept'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __c_accept(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            await ctx.send("Вы не ввели человека")
        elif not self.db.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
            await ctx.send(f"Такой игры не существует, посмотреть все ваши активные игры - "
                           f"{settings['prefix']}games")
        elif reladdons.long.minutes(self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Date")) > 5:
            await ctx.send(f"Время истекло:(")
            self.db.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
        elif self.db.get_cash(ctx.author.id, ctx.guild.id) < \
                self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash"):
            await ctx.send(f"{ctx.author.mention}, У Вас недостаточно средств")
        elif self.db.get_cash(member.id, ctx.guild.id) < \
                self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash"):
            await ctx.send(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
        else:
            self.num = self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash")
            self.db.take_coins(ctx.author.id, ctx.guild.id, self.num)
            self.db.take_coins(member.id, ctx.guild.id, self.num)
            self.ch = random.randint(1, 2)
            # if member.id == 401555829620211723:
            #       self.ch = 2
            if self.ch == 1:
                self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
                self.emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(self.num * 2)}** DP коинов!',
                    inline=False
                )
                await ctx.send(embed=self.emb)
                self.db.add_coins(ctx.author.id, ctx.guild.id, self.num * 2)
                self.db.add_lose(member.id, ctx.guild.id)
                self.db.add_win(member.id, ctx.guild.id, null=True)
                self.db.add_win(ctx.author.id, ctx.guild.id)
                self.db.add_lose(ctx.author.id, ctx.guild.id, null=True)
                await self.db.achievement_member(member)
                await self.db.achievement(ctx)
                await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "WinsCount", self.num * 2)
                self.db.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "LosesCount", self.num * 2
                )
            else:
                self.db.add_lose(ctx.author.id, ctx.guild.id)
                self.db.add_win(ctx.author.id, ctx.guild.id, null=True)
                self.db.add_win(member.id, ctx.guild.id)
                self.db.add_lose(member.id, ctx.guild.id, null=True)
                await self.db.achievement_member(member)
                await self.db.achievement(ctx)
                self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
                self.emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{member.mention}, Вы выиграли **{divide_the_number(self.num * 2)}** DP коинов!',
                    inline=False
                )
                await ctx.send(embed=self.emb)
                self.db.add_coins(member.id, member.guild.id, self.num * 2)
                self.db.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "WinsCount", self.num * 2
                )
                await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "LosesCount", self.num * 2)
            self.db.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
