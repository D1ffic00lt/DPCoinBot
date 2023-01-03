import random

from datetime import datetime
from discord.ext import commands
from typing import Union

from database.db import Database
from botsections.functions.additions import get_time, write_log
from config import (
    VALENTINES_DAY_MIN_PRICE,
    VALENTINES_DAY_MAX_PRICE
)
__all__ = (
    "ValentinesDay",
)


class ValentinesDay(commands.Cog):
    NAME = 'ValentinesDay module'

    __slots__ = (
        "bot", "db", "prize", "valentine"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.db = db
        self.valentine: int = 0
        self.prize: int = 0
        print(f"[{get_time()}] [INFO]: ValentinesDay event connected")
        write_log(f"[{get_time()}] [INFO]: ValentinesDay event connected")

    @commands.command(aliases=["val_open"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __val_open(self, ctx, count: Union[int, str] = None) -> None:
        if int(datetime.today().strftime('%m')) == 2 and int(datetime.today().strftime('%d')) == 14:
            self.valentine = self.db.get_from_inventory(ctx.author.id, ctx.guild.id, "Valentines")
            if self.valentine == 0:
                await ctx.reply("У Вас нет валентинок:(")
                return
            if isinstance(count, int):
                if int(count) > self.valentine:
                    await ctx.reply("У Вас недостаточно валентинок:(\nУ Вас {} валентинок".format(self.valentine))
                    return
                elif int(count) <= 0:
                    await ctx.reply(f"{ctx.author.mention}, Вы не можете отрыть 0(ну или меньше) валентинок:)")
                    return
            if count is None:
                self.prize = random.randint(VALENTINES_DAY_MIN_PRICE, VALENTINES_DAY_MAX_PRICE)
                self.db.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                self.db.update_inventory(ctx.author.id, ctx.guild.id, "Valentines", -1)
                await ctx.reply(f"{ctx.author.mention}, из валентинки выпало {self.prize} коинов! Поздравляем!")
            elif count == "all":
                self.prize = sum(
                    random.randint(VALENTINES_DAY_MIN_PRICE, VALENTINES_DAY_MAX_PRICE)
                    for _ in range(self.valentine)
                )
                self.db.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                self.db.update_inventory(ctx.author.id, ctx.guild.id, "Valentines", -self.valentine)
                await ctx.reply(f"{ctx.author.mention}, из валентинок выпало {self.prize} коинов! Поздравляем!")
            else:
                self.prize = sum(
                    random.randint(VALENTINES_DAY_MIN_PRICE, VALENTINES_DAY_MAX_PRICE)
                    for _ in range(count)
                )
                self.db.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                self.db.update_inventory(ctx.author.id, ctx.guild.id, "Valentines", -count)
                await ctx.reply(f"{ctx.author.mention}, из валентинок выпало {self.prize} коинов! Поздравляем!")
