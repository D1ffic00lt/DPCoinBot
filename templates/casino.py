import random

import discord
from discord.ext import commands
from reladdons import razr

from ..database.db import Database
from ..config import settings
from .helperfunction import create_emb


class Casino(commands.Cog, name='Casino module', Database):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.casino = settings["casino"]

    @commands.command(aliases=['rust_casino'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_3(self, ctx, num: int = None, count: int = None):
        if self.is_the_casino_allowed(ctx.message.channel.id):
            if num is None:
                await ctx.send("Вы ну ввели Вашу ставку!")
            elif num <= 0:
                await ctx.send("Вы не можете поставить отрицательную ставку и 0!")
            elif self.get_cash(ctx.author.id, ctx.guild.id) < num:
                await ctx.send("У Вас не достаточно денег для этой ставки!")
            else:
                if count is None:
                    await ctx.send("Вы ну ввели на какое число вы ставите! Либо 1, либо 3, либо 5, либо 10, либо 20!")
                else:
                    if count == 1 or count == 3 or count == 5 or count == 10 or count == 20:
                        random.shuffle(self.casino)
                        if self.casino[0] == count:
                            if self.casino[0] == 1:
                                self.take_coins(ctx.author.id, ctx.guild.id, num)
                                num *= 2
                                self.add_coins(ctx.author.id, ctx.guild.id, num)
                                color = [role for role in ctx.author.roles][-1].color
                                if str([role for role in ctx.author.roles][-1]) == "@everyone":
                                    color = discord.Color.from_rgb(32, 34, 37)
                                await ctx.send(embed=create_emb(title="🎰Вы выиграли!🎰", color=color, args=[
                                    {"name": f'Поздравляем!',
                                     "value": f'{ctx.author.mention}, '
                                              f'Вы выиграли **{razr(num)}** DP коинов!',
                                     "inline": False}]))
                                wp = "Win "
                                await self.stats_update(ctx, "rust_casinos", "rc", "wins", num)

                        else:
                            self.take_coins(ctx.author.id, ctx.guild.id, num)
                            num = self.casino[0] * num
                            color = [role for role in ctx.author.roles][-1].color
                            if str([role for role in ctx.author.roles][-1]) == "@everyone":
                                color = discord.Color.from_rgb(32, 34, 37)
                            await ctx.send(embed=create_emb(title="🎰Вы выиграли!🎰", color=color, args=[
                                {"name": f'Поздравляем!',
                                 "value": f'{ctx.author.mention}, '
                                          f'Вы выиграли **{razr(num)}** DP коинов!',
                                 "inline": False}]))
                            self.add_coins(ctx.author.id, ctx.guild.id, num)
                            wp = "Win "
                            await self.stats_update(ctx, "rust_casinos", "rc", "wins", num)

                    elif self.casino[0] != count:
                        self.take_coins(ctx.author.id, ctx.guild.id, num)
                        wp = "Lose"
                        num = -num
                        color = [role for role in ctx.author.roles][-1].color
                        if str([role for role in ctx.author.roles][-1]) == "@everyone":
                            color = discord.Color.from_rgb(32, 34, 37)
                        await ctx.send(embed=create_emb(title="🎰Вы выиграли!🎰", color=color, args=[
                            {"name": f'Поздравляем!',
                             "value": f'{ctx.author.mention}, '
                                      f'Вы выиграли **{razr(num)}** DP коинов!',
                             "inline": False}]))
                        await self.stats_update(ctx, "rust_casinos", "rc", "loses", num)

                    else:
                        await ctx.send(
                            f"{ctx.author.mention}, Вы должны поставить либо 1, либо 3, либо 5, либо 10, либо 20!")
        else:
            await ctx.send(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")
