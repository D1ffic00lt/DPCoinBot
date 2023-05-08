# -*- coding: utf-8 -*-
import logging
import random
import discord

from typing import List, Dict
from discord.ext import commands

from units.additions import (
    fail_rand, get_color, divide_the_number,
    casino2ch, get_time, choice, total_minutes
)
from units.texts import *
from config import PREFIX

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

    def __init__(self, bot: commands.Bot, db, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.bot: commands.Bot = bot
        self.casino: Dict[int, Dict[str, list]] = {}
        self.rust_casino: List[int] = casino_rust.copy()
        self.texts: dict = {}
        logging.info(f"Casino connected")

    @commands.command(aliases=['rust_casino'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_3(
            self, ctx: commands.context.Context,
            bid: int = None, number: int = None
    ) -> None:
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.reply("Вы ну ввели Вашу ставку!")
            elif bid <= 0:
                await ctx.reply("Вы не можете поставить ставку, которая меньше 1!")
            elif self.db.get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.reply("У Вас не достаточно денег для этой ставки!")
            else:
                if number is None:
                    await ctx.reply("Вы не ввели число! (Либо 1, либо 3, либо 5, либо 10, либо 20)")
                else:
                    color = get_color(ctx.author.roles)
                    random.shuffle(self.rust_casino)
                    logging.info(self.rust_casino)
                    if number in [1, 3, 5, 10, 20]:
                        self.db.take_coins(ctx.author.id, ctx.guild.id, bid)

                        if self.rust_casino[0] == number:
                            self.db.add_coins(ctx.author.id, ctx.guild.id, (self.rust_casino[0] * bid))
                            emb = discord.Embed(
                                title="🎰Вы выиграли!🎰",
                                colour=color
                            )
                            emb.add_field(
                                name=f'Поздравляем!',
                                value=f'{ctx.author.mention}, '
                                      f'Вы выиграли **{divide_the_number(self.rust_casino[0] * bid)}** '
                                      f'DP коинов!',
                                inline=False
                            )
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RustCasinosCount", "RustCasino", "WinsCount", bid)
                        elif self.rust_casino[0] != number:
                            emb = discord.Embed(
                                title="🎰Вы проиграли!🎰",
                                colour=color
                            )
                            emb.add_field(
                                name=f'Вы проиграли:(',
                                value=f'{ctx.author.mention}, выпало число {self.rust_casino[0]}',
                                inline=False
                            )
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RustCasinosCount", "RustCasino", "LosesCount", -bid)
                    else:
                        await ctx.reply(
                            f"{ctx.author.mention}, Вы должны поставить либо 1, либо 3, либо 5, либо 10, либо 20!"
                        )
        else:
            await ctx.reply(
                f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!"
                       )

    @commands.command(aliases=['fail'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __fail(
            self, ctx: commands.context.Context,
            bid: int = None, coefficient: float = None
    ) -> None:
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.reply(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            elif coefficient is None:
                await ctx.reply(f"{ctx.author.mention}, Вы не ввели коэффициент")
            elif coefficient < 0.07:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить на коэффициент ниже 0.07")
            elif coefficient > 10:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить на коэффициент больше 10")
            elif self.db.get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.reply(f"{ctx.author.mention}, У Вас недостаточно средств")
            else:
                self.db.take_coins(ctx.author.id, ctx.guild.id, bid)
                dropped_coefficient = fail_rand(ctx.author.id)[0]
                color = get_color(ctx.author.roles)
                if dropped_coefficient < coefficient:
                    emb = discord.Embed(
                        title="🎰Вы проиграли!🎰" +
                              [" Вам выпал 0.00...🎰" if dropped_coefficient == 0 else ""][0],
                        colour=color
                    )
                    emb.add_field(
                        name=f':(',
                        value=f'Выпало число `{dropped_coefficient}`\n{ctx.author}',
                        inline=False
                    )
                    await ctx.reply(embed=emb)
                    if dropped_coefficient == 0:
                        if not self.db.check_completion_dropping_zero_in_fail_achievement(ctx.author.id, ctx.guild.id):
                            self.db.add_coins(ctx.author.id, ctx.guild.id, 4000)
                            self.db.complete_dropping_zero_in_fail_achievement(ctx.author.id, ctx.guild.id)
                            try:
                                await ctx.author.reply(
                                    "Поздравляем, Вы забрали сумму которую поставили. А, нет, не забрали, "
                                    "разработчик до сих пор не пофиксил это...\nНу или пофиксил..."
                                    "\nВот тебе скромная награда! (4000 коинов)"
                                )
                            except discord.errors.Forbidden:
                                pass
                    await self.db.stats_update(ctx, "FailsCount", "Fails", "LosesCount", -bid)
                else:
                    self.db.add_coins(ctx.author.id, ctx.guild.id, bid + int(bid * coefficient))
                    emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                    emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value=f'Выпало число `{dropped_coefficient}`\n{ctx.author}, Вы выиграли '
                              f'**{divide_the_number(bid + int(bid * coefficient))}** DP коинов!',
                        inline=False
                    )
                    await ctx.reply(embed=emb)
                    await self.db.stats_update(ctx, "FailsCount", "Fails", "WinsCount", bid + int(bid * coefficient))
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['777'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino777(self, ctx: commands.context.Context, bid: int = None) -> None:
        if ctx.author.id != 0:
            return
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.reply(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            else:
                color = get_color(ctx.author.roles)
                result_bid = bid
                self.db.take_coins(ctx.author.id, ctx.guild.id, bid)
                line1 = choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=7,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                line2 = choice(
                    "7", "0", "8", "1",
                    output=3, shuffle_long=9,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                line3 = choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=8,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                if line2[1] == "8":
                    result_bid *= 2
                elif line2[1] == "0":
                    result_bid *= 3
                elif line2[1] == "7":
                    result_bid *= 5
                elif line2[1] == "1":
                    result_bid *= 1
                if line2[0] == line2[1] and line2[1] == line2[2]:
                    self.db.add_coins(ctx.author.id, ctx.guild.id, result_bid)
                    emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                    emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *line1[0], *line1[1], *line1[2],
                            *line2[0], *line2[1], *line2[2],
                            *line3[0], *line3[1], *line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await ctx.reply(embed=emb)
                    await self.db.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "WinsCount", result_bid)

                elif line1[2] == line2[1] and line2[1] == line3[0]:
                    self.db.add_coins(ctx.author.id, ctx.guild.id, result_bid)
                    emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                    emb.add_field(
                        name=f'🎰Вы выиграли!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *line1[0], *line1[1], *line1[2],
                            *line2[0], *line2[1], *line2[2],
                            *line3[0], *line3[1], *line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    self.db.add_coins(ctx.author.id, ctx.guild.id, result_bid)
                    await ctx.reply(embed=emb)
                    await self.db.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "WinsCount", result_bid)

                else:
                    emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=color)
                    emb.add_field(
                        name=f':(',
                        value='{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *line1[0], *line1[1], *line1[2],
                            *line2[0], *line2[1], *line2[2],
                            *line3[0], *line3[1], *line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await ctx.reply(embed=emb)
                    await self.db.stats_update(ctx, "ThreeSevensCount", "ThreeSevens", "LosesCount", -bid)

        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['coinflip'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_2(self, ctx: commands.context.Context, count: int = None, member: discord.Member = None):
        date_now = get_time()
        color = get_color(ctx.author.roles)
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if member is None:
                if await self.db.cash_check(ctx, count, min_cash=10, check=True):
                    self.db.take_coins(ctx.author.id, ctx.guild.id, count)
                    casino_num = casino2ch(ctx.author.id)[0]
                    if casino_num == 1:
                        emb = discord.Embed(title="Вы выиграли!", colour=color)
                        emb.add_field(
                            name=f'Поздравляем!',
                            value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(count * 2)}** DP коинов!',
                            inline=False
                        )
                        await ctx.reply(embed=emb)
                        self.db.add_coins(ctx.author.id, ctx.guild.id, count * 2)
                        await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "WinsCount", count * 2)

                    else:
                        emb = discord.Embed(title="Вы проиграли:(", colour=color)
                        emb.add_field(
                            name=f'Вы проиграли:(',
                            value=f'{ctx.author.mention}, значит в следующий раз',
                            inline=False
                        )
                        await ctx.reply(embed=emb)
                        await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "LosesCount", -count)

            elif member is not None:
                if count <= 9:
                    await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
                elif ctx.author.id == member.id:
                    await ctx.reply("Вы не можете играть с самим собой")
                elif count is None:
                    await ctx.reply(f"{ctx.author.mention}, Вы не ввели вашу ставку")
                elif self.db.get_cash(ctx.author.id, ctx.guild.id) < count:
                    await ctx.reply(f"{ctx.author.mention}, У Вас недостаточно средств")
                elif self.db.get_cash(member.id, ctx.guild.id) < count:
                    await ctx.reply(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
                else:
                    if self.db.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
                        await ctx.reply(
                            f"{ctx.author.mention}, такая игра уже существует! Для удаления - "
                            f"{PREFIX}del_games "
                            f"{member.mention}"
                        )
                    else:
                        self.db.insert_into_coinflip(
                            ctx.author.id, member.id,
                            str(ctx.author), str(member),
                            ctx.guild.id, str(ctx.guild),
                            count, str(date_now)
                        )
                        emb = discord.Embed(title=f"{member}, вас упомянули в коинфлипе!", colour=color)
                        emb.add_field(
                            name=f'Коинфлип на {count} DP коинов!',
                            value=f"{ctx.author.mention}, значит в следующий раз"
                                  f"{PREFIX}accept {ctx.author.mention}\n\nЧтобы отменить - "
                                  f"{PREFIX}reject {ctx.author.mention}",
                            inline=False
                        )
                        await ctx.reply(embed=emb)
                        await ctx.reply(member.mention)
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=["roll"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __roll(self, ctx: commands.context.Context, count: int = None, *args):
        color = get_color(ctx.author.roles)
        count = count
        if self.db.is_the_casino_allowed(ctx.message.channel.id):
            if await self.db.cash_check(ctx, count, min_cash=10, check=True):
                self.texts[ctx.author.id] = ""
                self.casino[ctx.author.id] = {}
                self.casino[ctx.author.id]["color"] = choice(
                    "black", "red", shuffle_long=37, key=str(ctx.author.id), array_long=37
                )
                self.casino[ctx.author.id]["number"] = (random.randint(0, 36), )
                # TODO: fix indexes
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
                        self.db.take_coins(ctx.author.id, ctx.guild.id, count)
                        if int(self.texts[ctx.author.id]) == 0 and int(self.texts[ctx.author.id][0]) \
                                == self.casino[ctx.author.id]["number"][0]:
                            count *= 35
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value='Выпало число {}, green\n{}'
                                      ", Вы выиграли **{}** DP коинов!!".format(
                                            self.casino[ctx.author.id]['number'][0],
                                            ctx.author.mention,
                                            divide_the_number(count)
                                        ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif int(self.texts[ctx.author.id]) == self.casino[ctx.author.id]["number"][0]:
                            count *= 35
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)
                        else:
                            emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=color)
                            emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы  проиграли:(".format(
                                            self.casino[ctx.author.id]['number'][0],
                                            self.casino[ctx.author.id]['color'][0],
                                            ctx.author.mention
                                        ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            count = -count
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "LosesCount", count)
                except ValueError:
                    if self.texts[ctx.author.id] in roll_types:
                        self.db.take_coins(ctx.author.id, ctx.guild.id, count)
                        if self.texts[ctx.author.id] == "1st12" and self.casino[ctx.author.id]["number"][0] <= 12:
                            count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "2nd12" and \
                                24 >= self.casino[ctx.author.id]["number"][0] > 12:
                            count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "3rd12" and self.casino[ctx.author.id]["number"][0] > 24:
                            count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "1to18" and \
                                0 != self.casino[ctx.author.id]["number"][0] <= 18:
                            count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "19to36" and \
                                18 < self.casino[ctx.author.id]["number"][0] <= 36:
                            count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "2to1" and self.casino[ctx.author.id]["number"][0] in row1:
                            count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "2to2" and self.casino[ctx.author.id]["number"][0] in row2:
                            count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "2to3" and self.casino[ctx.author.id]["number"][0] in row3:
                            count *= 3
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "b" and self.casino[ctx.author.id]["color"][0] == "black":
                            count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)

                        elif self.texts[ctx.author.id] == "r" and self.casino[ctx.author.id]["color"][0] == "red":
                            count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)
                        elif self.texts[ctx.author.id] == "ch" and self.casino[ctx.author.id]["number"][0] % 2 == 0:
                            count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)
                        elif self.texts[ctx.author.id] == "nch" and self.casino[ctx.author.id]["number"][0] % 2 == 1:
                            count *= 2
                            self.db.add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", count)
                        else:
                            emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=color)
                            emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы проиграли:(".format(
                                            self.casino[ctx.author.id]['number'][0],
                                            self.casino[ctx.author.id]['color'][0],
                                            ctx.author.mention
                                        ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self.db.stats_update(ctx, "RollsCount", "Rolls", "WinsCount", -count)

                    else:
                        await ctx.reply(f"{ctx.author.mention}, Такого атрибута не существует! ")
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['del_games'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __del_games(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            self.db.delete_from_coinflip(ctx.author.id, ctx.guild.id, ctx.guild.id)
            await ctx.message.add_reaction('✅')
        else:
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                self.db.delete_from_coinflip(member.id, member.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
            else:
                await ctx.reply("Ты чё ку-ку? Тебе так нельзя.")

    @commands.command(aliases=['reject'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __reject(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            await ctx.reply("Вы не ввели человека")
        elif member.id == ctx.author.id:
            await ctx.reply("Вы не можете ввести себя")
        elif not self.db.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
            await ctx.reply(
                f"Такой игры не существует, посмотреть все ваши активные игры - {PREFIX}games"
            )
        else:
            self.db.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['games'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __games(self, ctx: commands.context.Context):
        if not self.db.check_coinflip_games(ctx.author.id, ctx.guild.id):
            emb = discord.Embed(title="Активные коинфлипы")
            for row in self.db.get_player_active_coinflip(ctx.author.id, ctx.guild.id):
                emb.add_field(
                    name=f'{ctx.author} и {row[0]}',
                    value=f'Сумма: {row[1]}',
                    inline=False
                )
            for row in self.db.get_player_active_coinflip(ctx.author.id, ctx.guild.id, True):
                emb.add_field(
                    name=f'**{row[0]}** и **{ctx.author}**',
                    value=f'Сумма: **{row[1]}**',
                    inline=False
                )
            await ctx.reply(embed=emb)
        else:
            await ctx.reply("У Вас нет активных игр")

    @commands.command(aliases=['accept'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __c_accept(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            await ctx.reply("Вы не ввели человека")
        elif not self.db.get_active_coinflip(ctx.author.id, member.id, ctx.guild.id):
            await ctx.reply(
                f"Такой игры не существует, посмотреть все ваши активные игры - {PREFIX}games"
            )
        elif total_minutes(self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Date")) > 5:
            await ctx.reply(f"Время истекло:(")
            self.db.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
        elif self.db.get_cash(ctx.author.id, ctx.guild.id) < \
                self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash"):
            await ctx.reply(f"{ctx.author.mention}, У Вас недостаточно средств")
        elif self.db.get_cash(member.id, ctx.guild.id) < \
                self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash"):
            await ctx.reply(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
        else:
            num = self.db.get_from_coinflip(ctx.author.id, member.id, ctx.guild.id, "Cash")
            self.db.take_coins(ctx.author.id, ctx.guild.id, num)
            self.db.take_coins(member.id, ctx.guild.id, num)
            self.ch = random.randint(1, 2)
            # if member.id == 401555829620211723:
            #       self.ch = 2
            if self.ch == 1:
                emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
                emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(num * 2)}** DP коинов!',
                    inline=False
                )
                await ctx.reply(embed=emb)
                self.db.add_coins(ctx.author.id, ctx.guild.id, num * 2)
                self.db.add_lose(member.id, ctx.guild.id)
                self.db.add_win(member.id, ctx.guild.id, null=True)
                self.db.add_win(ctx.author.id, ctx.guild.id)
                self.db.add_lose(ctx.author.id, ctx.guild.id, null=True)
                await self.db.achievement_member(member)
                await self.db.achievement(ctx)
                await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "WinsCount", num * 2)
                self.db.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "LosesCount", num * 2
                )
            else:
                self.db.add_lose(ctx.author.id, ctx.guild.id)
                self.db.add_win(ctx.author.id, ctx.guild.id, null=True)
                self.db.add_win(member.id, ctx.guild.id)
                self.db.add_lose(member.id, ctx.guild.id, null=True)
                await self.db.achievement_member(member)
                await self.db.achievement(ctx)
                emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
                emb.add_field(
                    name=f'Поздравляем!',
                    value=f'{member.mention}, Вы выиграли **{divide_the_number(num * 2)}** DP коинов!',
                    inline=False
                )
                await ctx.reply(embed=emb)
                self.db.add_coins(member.id, member.guild.id, num * 2)
                self.db.stats_update_member(
                    member.id, member.guild.id, "CoinFlipsCount", "CoinFlips", "WinsCount", num * 2
                )
                await self.db.stats_update(ctx, "CoinFlipsCount", "CoinFlips", "LosesCount", num * 2)
            self.db.delete_from_coinflip(ctx.author.id, member.id, ctx.guild.id)
