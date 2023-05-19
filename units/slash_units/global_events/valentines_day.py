# -*- coding: utf-8 -*-
import logging
import random

from datetime import datetime
from typing import Callable

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import VALENTINES_DAY_MIN_PRIZE, VALENTINES_DAY_MAX_PRIZE
from database.user.users import User

__all__ = (
    "ValentinesDaySlash",
)


class ValentinesDaySlash(commands.Cog):
    NAME = 'ValentinesDay slash module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.session: Callable[[], AsyncSession] = session
        logging.info(f"ValentinesDay (Slash) event connected")

    @app_commands.command(name="val_open", description="Открыть валентинку")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __val_open(self, inter: discord.Interaction, count: int = None) -> None:
        if not (int(datetime.today().strftime('%m')) == 2 and int(datetime.today().strftime('%d')) == 14):
            return
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(
                        User.user_id == inter.user.id and User.guild_id == inter.guild.id
                    )
                )
                user: User | None = user.scalars().first()
                if not user:
                    return
                valentine = user.inventories[0].valentines
                if valentine == 0:
                    await inter.response.send_message("У Вас нет валентинок:(")
                    return
                if isinstance(count, int):
                    if int(count) > valentine:
                        await inter.response.send_message(
                            "У Вас недостаточно валентинок:(\nУ Вас {} валентинок".format(valentine)
                        )
                        return
                    elif int(count) <= 0:
                        await inter.response.send_message(
                            f"{inter.user.mention}, Вы не можете отрыть 0(ну или меньше) валентинок:)"
                        )
                        return
                if count is None:
                    prize = random.randint(VALENTINES_DAY_MIN_PRIZE, VALENTINES_DAY_MAX_PRIZE)
                    user.cash += prize
                    user.inventories[0].valentines -= 1
                    await inter.response.send_message(
                        f"{inter.user.mention}, из валентинки выпало {prize} коинов! Поздравляем!"
                    )
                elif count == "all":
                    prize = random.randint(
                        VALENTINES_DAY_MIN_PRIZE * valentine,
                        VALENTINES_DAY_MAX_PRIZE * valentine
                    )
                    user.cash += prize
                    user.inventories[0].valentines -= valentine
                    await inter.response.send_message(
                        f"{inter.user.mention}, из валентинок выпало {prize} коинов! Поздравляем!"
                    )
                else:
                    prize = random.randint(VALENTINES_DAY_MIN_PRIZE * count, VALENTINES_DAY_MAX_PRIZE * count)
                    user.cash += prize
                    user.inventories[0].valentines -= count
                    await inter.response.send_message(
                        f"{inter.user.mention}, из валентинок выпало {prize} коинов! Поздравляем!"
                    )
