import random
import discord
import reladdons

from discord.ext import commands

from ..database.db import Database
from ..config import settings
from .helperfunction import (
    create_emb, fail_rand,
    get_color, divide_the_number
)


class Casino(commands.Cog, name='Casino module', Database):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.result_bid: int
        self.bot: commands.Bot = bot
        self.casino: list = settings["casino"]
        self.color: discord.Color
        self.dropped_coefficient: float
        self.line1: list
        self.line2: list
        self.line3: list

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
                await ctx.send("Вы не можете поставить отрицательную ставку и 0!")
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
                            self.add_coins(ctx.author.id, ctx.guild.id, self.casino[0] * bid)
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
                            await self.stats_update(ctx, "rust_casinos", "rc", "wins", bid)
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
                        await self.stats_update(ctx, "rust_casinos", "rc", "loses", -bid)

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
                    await self.stats_update(ctx, "fails", "f", "loses", -bid)
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
                    await self.stats_update(ctx, "fails", "f", "wins", bid * coefficient)
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
                    await self.stats_update(ctx, "ssss", "s", "wins", self.result_bid)
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
                                    "value": '`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP '
                                             'коинов!'.format(
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
                    await self.stats_update(ctx, "ssss", "s", "wins", self.result_bid)

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
                    await self.stats_update(ctx, "ssss", "s", "loses", -bid)

        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")
