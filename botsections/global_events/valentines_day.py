import random

from datetime import datetime
from discord.ext import commands
from typing import Union

from botsections.database.db import Database


class Casino(commands.Cog, name='Casino module', Database):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("server.db")
        self.bot: commands.Bot = bot

    @commands.command(aliases=["val_open"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __val_open(self, ctx, count: Union[int, str] = None) -> None:
        if int(datetime.today().strftime('%m')) == 2 and int(datetime.today().strftime('%d')) == 14:
            self.valentine = self.get_from_inventory(ctx.author.id, ctx.guild.id, "Valentines")
            if self.valentine == 0:
                await ctx.send("У Вас нет валентинок:(")
                return
            if isinstance(count, int):
                if int(count) > self.valentine:
                    await ctx.send("У Вас недостаточно валентинок:(\nУ Вас {} валентинок".format(self.valentine))
                    return
                elif int(count) <= 0:
                    await ctx.send(f"{ctx.author.mention}, Вы не можете отрыть 0(ну или меньше) валентинок:)")
                    return
            if count is None:
                self.prize = random.randint(1000, 6000)
                self.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                self.update_inventory(ctx.author.id, ctx.guild.id, "Valentines", -1)
                await ctx.send(f"{ctx.author.mention}, из валентинки выпало {self.prize} коинов! Поздравляем!")
            elif count == "all":
                self.prize = sum(random.randint(100, 6000) for _ in range(self.valentine))
                self.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                self.update_inventory(ctx.author.id, ctx.guild.id, "Valentines", -self.valentine)
                await ctx.send(f"{ctx.author.mention}, из валентинок выпало {self.prize} коинов! Поздравляем!")
            else:
                self.prize = sum(random.randint(100, 6000) for _ in range(count))
                self.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                self.update_inventory(ctx.author.id, ctx.guild.id, "Valentines", -count)
                await ctx.send(f"{ctx.author.mention}, из валентинок выпало {self.prize} коинов! Поздравляем!")
