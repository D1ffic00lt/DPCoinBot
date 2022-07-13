# -*- coding: utf-8 -*-
from __future__ import annotations

import random

import discord
import reladdons

from discord.ext import commands
from typing import List, Union

from botsections.database.db import Database
from botsections.helperfunction import (
    create_emb, fail_rand, logging,
    get_color, divide_the_number, casino2ch, get_time
)
from botsections.texts import *


class Casino(commands.Cog, Database, name='Casino module'):
    @logging
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("../server.db")
        self.bot: commands.Bot = bot
        self.result_bid: int
        self.casino: List[Union[list, dict]] = []
        self.rust_casino: List[int] = casino
        self.color: discord.Color
        self.dropped_coefficient: float
        self.line1: List[int]
        self.line2: List[int]
        self.line3: List[int]
        self.texts: dict = {}

        print("Casino connected")

    @commands.command(aliases=['rust_casino'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_3(
            self,
            ctx: commands.context.Context,
            bid: int = None,
            number: int = None
    ) -> None:
        if self.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.send("Вы ну ввели Вашу ставку!")
            elif bid <= 0:
                await ctx.send("Вы не можете поставить ставку, которая меньше 1!")
            elif self.get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.send("У Вас не достаточно денег для этой ставки!")
            else:
                if number is None:
                    await ctx.send("Вы ну ввели на какое число вы ставите! Либо 1, либо 3, либо 5, либо 10, либо 20!")
                else:
                    if number in [1, 3, 5, 10, 20]:
                        self.take_coins(ctx.author.id, ctx.guild.id, bid)
                        self.color = get_color(ctx.author.roles)
                        random.shuffle(self.casino)
                        if self.casino[0] == number:
                            self.add_coins(ctx.author.id, ctx.guild.id, (self.rust_casino[0] * bid))
                            await ctx.send(
                                embed=create_emb(
                                    title="🎰Вы выиграли!🎰",
                                    color=self.color,
                                    args=[
                                        {
                                            "name": f'Поздравляем!',
                                            "value": f'{ctx.author.mention}, '
                                                     f'Вы выиграли **{divide_the_number(self.casino[0] * bid)}** '
                                                     f'DP коинов!',
                                            "inline": False
                                        }
                                    ]
                                )
                            )
                            await self.stats_update(ctx, "RustCasinosCount", "RustCasino", "WinsCount", bid)
                    elif self.casino[0] != number:
                        await ctx.send(
                            embed=create_emb(
                                title="🎰Вы проиграли!🎰",
                                color=self.color,
                                args=[
                                    {
                                        "name": f'Вы проиграли:(',
                                        "value": f'{ctx.author.mention}, выпало число {self.casino[0]}',
                                        "inline": False
                                    }
                                ]
                            )
                        )
                        await self.stats_update(ctx, "RustCasinosCount", "RustCasino", "LosesCount", -bid)

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
            self,
            ctx: commands.context.Context,
            bid: int = None,
            coefficient: float = None
    ) -> None:
        if self.is_the_casino_allowed(ctx.message.channel.id):
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
            elif self.get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.send(f"{ctx.author.mention}, У Вас недостаточно средств")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, bid)
                self.dropped_coefficient = fail_rand(ctx.author.id)[0]
                self.color = get_color(ctx.author.roles)
                if self.dropped_coefficient > coefficient:
                    await ctx.send(
                        embed=create_emb(
                            title="🎰Вы проиграли!🎰" +
                                  [" Вам выпал 0.00...🎰" if self.dropped_coefficient == 0 else ""][0],
                            color=self.color,
                            args=[
                                {
                                    "name": f':(',
                                    "value": f'Выпало число `{self.dropped_coefficient}`\n{ctx.author}',
                                    "inline": False
                                }
                            ]
                        )
                    )
                    await self.stats_update(ctx, "FailsCount", "Fails", "LosesCount", -bid)
                    if self.dropped_coefficient == 0:
                        if not self.check_completion_dropping_zero_in_fail_achievement(ctx.author.id, ctx.guild.id):
                            self.add_coins(ctx.author.id, ctx.guild.id, 4000)
                            self.complete_dropping_zero_in_fail_achievement(ctx.author.id, ctx.guild.id)
                            try:
                                await ctx.author.send(
                                    "Поздравляем, Вы забрали сумму которую поставили. А, нет, не забрали, "
                                    "разработчик до сих пор не пофиксил это...\nНу или пофиксил..."
                                    "\nВот тебе скромная награда! (4000 коинов)"
                                )
                            except discord.errors.Forbidden:
                                pass
                else:
                    self.add_coins(ctx.author.id, ctx.guild.id, int(bid * coefficient))
                    await ctx.send(
                        embed=create_emb(
                            title="🎰Вы выиграли!🎰",
                            color=self.color,
                            args=[
                                {
                                    "name": f'🎰Поздравляем!🎰',
                                    "value": f'Выпало число `{self.dropped_coefficient}`\n{ctx.author}, Вы выиграли '
                                             f'**{divide_the_number(int(bid * coefficient))}** DP коинов!"',
                                    "inline": False
                                }
                            ]
                        )
                    )
                    await self.stats_update(ctx, "FailsCount", "Fails", "WinsCount", bid * coefficient)
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['777'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __casino777(self, ctx: commands.context.Context, bid: int = None) -> None:
        if self.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.send(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.send(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            else:
                self.color = get_color(ctx.author.roles)
                self.result_bid = bid
                self.take_coins(ctx.author.id, ctx.guild.id, bid)
                self.line1 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=7,
                    array_long=5,
                    key=ctx.author.id
                )
                self.line2 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3, shuffle_long=9,
                    array_long=5,
                    key=ctx.author.id
                )
                self.line3 = reladdons.randoms.choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=8,
                    array_long=5,
                    key=ctx.author.id
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
                    self.add_coins(ctx.author.id, ctx.guild.id, self.result_bid)
                    await self.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "WinsCount", self.result_bid)
                    await ctx.send(
                        embed=create_emb(
                            title="🎰Вы выиграли!🎰",
                            color=self.color,
                            args=[
                                {
                                    "name": f'🎰Поздравляем!🎰',
                                    "value": '`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, '
                                             'Вы выиграли **{}** DP коинов!'.format(
                                        *self.line1[0], *self.line1[1], *self.line1[2],
                                        *self.line2[0], *self.line2[1], *self.line2[2],
                                        *self.line3[0], *self.line3[1], *self.line3[2],
                                        ctx.author.mention, divide_the_number(bid)
                                    ),
                                    "inline": False
                                }
                            ]
                        )
                    )
                elif self.line1[2] == self.line2[1] and self.line2[1] == self.line3[0]:
                    self.add_coins(ctx.author.id, ctx.guild.id, self.result_bid)
                    await ctx.send(
                        embed=create_emb(
                            title="🎰Вы выиграли!🎰",
                            color=self.color,
                            args=[
                                {
                                    "name": f'🎰Поздравляем!🎰',
                                    "value": '`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, '
                                             'Вы выиграли **{}** DP коинов!'.format(
                                        *self.line1[0], *self.line1[1], *self.line1[2],
                                        *self.line2[0], *self.line2[1], *self.line2[2],
                                        *self.line3[0], *self.line3[1], *self.line3[2],
                                        ctx.author.mention, divide_the_number(bid)
                                    ),
                                    "inline": False
                                }
                            ])
                    )
                    self.add_coins(ctx.author.id, ctx.guild.id, self.result_bid)
                    await self.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "WinsCount", self.result_bid)

                else:
                    await ctx.send(
                        embed=create_emb(
                            title="🎰Вы проиграли:(🎰",
                            color=self.color, args=[
                                {
                                    "name": f':(',
                                    "value": '`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}'.format(
                                        *self.line1[0], *self.line1[1], *self.line1[2],
                                        *self.line2[0], *self.line2[1], *self.line2[2],
                                        *self.line3[0], *self.line3[1], *self.line3[2],
                                        ctx.author.mention
                                    ),
                                    "inline": False
                                }
                            ]
                        )
                    )
                    await self.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "LosesCount", -bid)

        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['coinflip'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def __casino_2(self, ctx: commands.context.Context, count: int = None, member: discord.Member = None):
        self.date_now = get_time()
        self.color = get_color(ctx.author.roles)
        if self.is_the_casino_allowed(ctx.message.channel.id):
            if member is None:
                if await self.cash_check(ctx, count, min_cash=10, check=True):
                    self.take_coins(ctx.author.id, ctx.guild.id, count)
                    self.casino_num = casino2ch(ctx.author.id)[0]
                    if self.casino_num == 1:
                        self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                        self.emb.add_field(
                            name=f'Поздравляем!',
                            value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(count * 2)}** DP коинов!',
                            inline=False
                        )
                        await ctx.send(embed=self.emb)
                        self.add_coins(ctx.author.id, ctx.guild.id, count * 2)
                        await self.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "WinsCount", count * 2)

                    else:
                        self.emb = discord.Embed(title="Вы проиграли:(", colour=self.color)
                        self.emb.add_field(
                            name=f'Вы проиграли:(',
                            value=f'{ctx.author.mention}, значит в следующий раз',
                            inline=False
                        )
                        await ctx.send(embed=self.emb)
                        await self.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "LosesCount", -count)

            elif member is not None:
                if count <= 9:
                    await ctx.send(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
                elif ctx.author.id == member.id:
                    await ctx.send("Вы не можете играть с самим собой")
                elif count is None:
                    await ctx.send(f"{ctx.author.mention}, Вы не ввели вашу ставку")
                elif self.get_cash(ctx.author.id, ctx.guild.id) < count:
                    await ctx.send(f"{ctx.author.mention}, У Вас недостаточно средств")
                elif self.get_cash(member.id, ctx.guild.id) < count:
                    await ctx.send(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
                else:
                    if self.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
                        await ctx.send(
                            f"{ctx.author.mention}, такая игра уже существует! Для удаления - "
                            f"{settings['prefix']}del_games "
                            f"{member.mention}"
                        )
                    else:
                        self.insert_into_coinflip(
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
        if self.is_the_casino_allowed(ctx.message.channel.id):
            if await self.cash_check(ctx, count, min_cash=10, check=True):
                self.texts[ctx.author.id] = ""
                self.casino[ctx.author.id] = {}
                self.casino[ctx.author.id]["color"] = reladdons.randoms.choice(
                    "black", "red", shuffle_long=37, key=ctx.author.id, array_long=37
                )
                self.casino[ctx.author.id]["number"] = reladdons.randoms.randint(
                    0, 36, key=ctx.author.id, shuffle_long=37, array_long=37
                )
                # casino2[ctx.author.id]["number"] = 1, [random.randint(0, 36), random.randint(0, 36)]
                for i in args:
                    self.texts[ctx.author.id] += i
                try:
                    self.casino[ctx.author.id]["color"][0] = casino_numbers_color[
                        self.casino[ctx.author.id]["number"][0]
                    ]
                    int(self.texts[ctx.author.id])
                    if int(self.texts[ctx.author.id][0]) < 0:
                        pass
                    elif int(self.texts[ctx.author.id][0]) > 36:
                        pass
                    else:
                        self.take_coins(ctx.author.id, ctx.guild.id, count)
                        if int(self.texts[ctx.author.id]) == 0 and int(self.texts[ctx.author.id][0]) \
                                == self.casino[ctx.author.id]["number"][0]:
                            count *= 35
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value='Выпало число {}, green\n{}'
                                      ", Вы выиграли **{}** DP коинов!!".format(
                                    self.casino[ctx.author.id]['number'][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif int(self.texts[ctx.author.id]) == self.casino[ctx.author.id]["number"][0]:
                            count *= 35
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
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
                            count = -count
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "LosesCount", count)
                except ValueError:
                    if self.texts[ctx.author.id] in roll_types:
                        self.take_coins(ctx.author.id, ctx.guild.id, count)
                        if self.texts[ctx.author.id] == "1st12" and self.casino[ctx.author.id]["number"][0] <= 12:
                            count *= 3
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "2nd12" and \
                                24 >= self.casino[ctx.author.id]["number"][0] > 12:
                            count *= 3
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
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

                        elif self.texts[ctx.author.id] == "3rd12" and self.casino[ctx.author.id]["number"][0] > 24:
                            count *= 3
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "1to18" and \
                                0 != self.casino[ctx.author.id]["number"][0] <= 18:
                            count *= 2
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "19to36" and \
                                18 < self.casino[ctx.author.id]["number"][0] <= 36:
                            count *= 2
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "2to1" and self.casino[ctx.author.id]["number"][0] in row1:
                            count *= 3
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "2to2" and self.casino[ctx.author.id]["number"][0] in row2:
                            count *= 3
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "2to3" and self.casino[ctx.author.id]["number"][0] in row3:
                            count *= 3
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "b" and self.casino[ctx.author.id]["color"][0] == "black":
                            count *= 2
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "r" and self.casino[ctx.author.id]["color"][0] == "red":
                            count *= 2
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=self.color)
                            self.emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)
                        elif self.texts[ctx.author.id] == "ch" and self.casino[ctx.author.id]["number"][0] % 2 == 0:
                            count *= 2
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

                        elif self.texts[ctx.author.id] == "nch" and self.casino[ctx.author.id]["number"][0] % 2 == 1:
                            count *= 2
                            self.add_coins(ctx.author.id, ctx.guild.id, count)
                            await self.stats_update(ctx, "RollsCounts", "Rolls", "WinsCount", count)
                            self.emb = discord.Embed(title="Вы выиграли!", colour=self.color)
                            self.emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0], *self.casino[ctx.author.id]["color"],
                                    ctx.author.mention, divide_the_number(count)),
                                inline=False)
                            await ctx.send(embed=self.emb)

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
                            await self.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", -count)

                    else:
                        await ctx.send(f"{ctx.author.mention}, Такого атрибута не существует! ")
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['del_games'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __del_games(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            self.delete_from_coinflip(ctx.author.id, ctx.guild.id, ctx.guild.id)
            await ctx.message.add_reaction('✅')
        else:
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                self.delete_from_coinflip(member.id, member.id, ctx.guild.id)
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
            self.get_active_coinflip()
        elif not self.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
            await ctx.send(f"Такой игры не существует, посмотреть все ваши активные игры - "
                           f"{settings['prefix']}games")
        else:
            self.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['games'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def __games(self, ctx: commands.context.Context):
        if not self.check_coinflip_games(ctx.author.id, ctx.guild.id):
            self.emb = discord.Embed(title="Активные коинфлипы")
            for row in self.get_player_active_coinflip(ctx.author.id, ctx.guild.id):
                self.emb.add_field(
                    name=f'{ctx.author} и {row[0]}',
                    value=f'Сумма: {row[1]}',
                    inline=False
                )
            for row in self.get_player_active_coinflip(ctx.author.id, ctx.guild.id, True):
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
        elif not self.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
            await ctx.send(f"Такой игры не существует, посмотреть все ваши активные игры - "
                           f"{settings['prefix']}games")
        elif reladdons.long.minutes(self.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Date")) > 5:
            await ctx.send(f"Время истекло:(")
            self.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
        elif self.get_cash(ctx.author.id, ctx.guild.id) < \
                self.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash"):
            await ctx.send(f"{ctx.author.mention}, У Вас недостаточно средств")
        elif self.get_cash(member.id, ctx.guild.id) < \
                self.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash"):
            await ctx.send(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
        else:
            self.num = self.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash")
            self.take_coins(ctx.author.id, ctx.guild.id, self.num)
            self.take_coins(member.id, ctx.guild.id, self.num)
            ch = random.randint(1, 2)
            # if member.id == 401555829620211723:
            #       ch = 2
            if ch == 1:
                self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
                self.emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(self.num * 2)}** DP коинов!',
                    inline=False
                )
                await ctx.send(embed=self.emb)
                self.add_coins(ctx.author.id, ctx.guild.id, self.num * 2)
                await self.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "WinsCount", self.num * 2)
                self.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "LosesCount", self.num * 2
                )
                self.add_lose(member.id, ctx.guild.id)
                self.add_win(member.id, ctx.guild.id, null=True)
                self.add_win(ctx.author.id, ctx.guild.id)
                self.add_lose(ctx.author.id, ctx.guild.id, null=True)
                await self.achievement_member(member)
                await self.achievement(ctx)
            else:
                self.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "WinsCount", self.num * 2
                )
                await self.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "LosesCount", self.num * 2)
                self.add_lose(ctx.author.id, ctx.guild.id)
                self.add_win(ctx.author.id, ctx.guild.id, null=True)
                self.add_win(member.id, ctx.guild.id)
                self.add_lose(member.id, ctx.guild.id, null=True)
                await self.achievement_member(member)
                await self.achievement(ctx)
                self.emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
                self.emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{member.mention}, Вы выиграли **{divide_the_number(self.num * 2)}** DP коинов!',
                    inline=False
                )
                await ctx.send(embed=self.emb)
                self.add_coins(member.id, member.guild.id, self.num * 2)
            self.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
