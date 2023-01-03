import random

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from database.db import Database
from botsections.functions.additions import get_time, write_log
from config import VALENTINES_DAY_MIN_PRICE, VALENTINES_DAY_MAX_PRICE
__all__ = (
    "ValentinesDaySlash",
)


class ValentinesDaySlash(commands.Cog):
    NAME = 'ValentinesDay slash module'

    __slots__ = (
        "bot", "db", "prize", "valentine"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.db = db
        self.valentine: int = 0
        self.prize: int = 0
        print(f"[{get_time()}] [INFO]: ValentinesDaySlash event connected")
        write_log(f"[{get_time()}] [INFO]: ValentinesDaySlash event connected")

    @app_commands.command(name="val_open", description="Открыть валентинку")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __val_open(self, inter: discord.Interaction, count: int = None) -> None:
        if int(datetime.today().strftime('%m')) == 2 and (9 < int(datetime.today().strftime('%d')) < 15):
            self.valentine = self.db.get_from_inventory(inter.user.id, inter.guild.id, "Valentines")
            if self.valentine == 0:
                await inter.response.send_message(
                    "У Вас нет валентинок:(", ephemeral=True
                )
                return
            if isinstance(count, int):
                if int(count) > self.valentine:
                    await inter.response.send_message(
                        "У Вас недостаточно валентинок:(\nУ Вас {} валентинок".format(self.valentine),
                        ephemeral=True
                    )
                    return
                elif int(count) <= 0:
                    await inter.response.send_message(
                        f"{inter.user.mention}, Вы не можете отрыть 0(ну или меньше) валентинок:)",
                        ephemeral=True
                    )
                    return
            if count is None:
                self.prize = random.randint(VALENTINES_DAY_MIN_PRICE, VALENTINES_DAY_MAX_PRICE)
                self.db.add_coins(inter.user.id, inter.guild.id, self.prize)
                self.db.update_inventory(inter.user.id, inter.guild.id, "Valentines", -1)
                await inter.response.send_message(
                    f"{inter.user.mention}, из валентинки выпало {self.prize} коинов! Поздравляем!"
                )
            elif count == "all":
                self.prize = random.randint(
                    VALENTINES_DAY_MIN_PRICE * self.valentine,
                    VALENTINES_DAY_MAX_PRICE * self.valentine
                )
                self.db.add_coins(inter.user.id, inter.guild.id, self.prize)
                self.db.update_inventory(inter.user.id, inter.guild.id, "Valentines", -self.valentine)
                await inter.response.send_message(
                    f"{inter.user.mention}, из валентинок выпало {self.prize} коинов! Поздравляем!"
                )
            else:
                self.prize = random.randint(VALENTINES_DAY_MIN_PRICE * count, VALENTINES_DAY_MAX_PRICE * count)
                self.db.add_coins(inter.user.id, inter.guild.id, self.prize)
                self.db.update_inventory(inter.user.id, inter.guild.id, "Valentines", -count)
                await inter.response.send_message(
                    f"{inter.user.mention}, из валентинок выпало {self.prize} коинов! Поздравляем!"
                )
