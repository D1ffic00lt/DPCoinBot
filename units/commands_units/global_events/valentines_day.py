# -*- coding: utf-8 -*-
import logging
import random

from datetime import datetime
from discord.ext import commands
from typing import Union, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import (
    VALENTINES_DAY_MIN_PRIZE,
    VALENTINES_DAY_MAX_PRIZE
)
__all__ = (
    "ValentinesDay",
)

from database.user.users import User


class ValentinesDay(commands.Cog):
    NAME = 'ValentinesDay module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.session: Callable[[], AsyncSession] = session
        logging.info(f"ValentinesDay event connected")

    @commands.command(aliases=["val_open"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __val_open(self, ctx, count: Union[int, str] = None) -> None:
        if not (int(datetime.today().strftime('%m')) == 2 and int(datetime.today().strftime('%d')) == 14):
            return
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(
                        User.user_id == ctx.author.id and User.guild_id == ctx.guild.id
                    )
                )
                user: User | None = user.scalars().first()
                if not user:
                    return
                valentine = user.inventories[0].valentines
                if valentine == 0:
                    await ctx.reply("У Вас нет валентинок:(")
                    return
                if isinstance(count, int):
                    if int(count) > valentine:
                        await ctx.reply("У Вас недостаточно валентинок:(\nУ Вас {} валентинок".format(valentine))
                        return
                    elif int(count) <= 0:
                        await ctx.reply(f"{ctx.author.mention}, Вы не можете отрыть 0(ну или меньше) валентинок:)")
                        return
                if count is None:
                    prize = random.randint(VALENTINES_DAY_MIN_PRIZE, VALENTINES_DAY_MAX_PRIZE)
                    user.cash += prize
                    user.inventories[0].valentines -= 1
                    await ctx.reply(f"{ctx.author.mention}, из валентинки выпало {prize} коинов! Поздравляем!")
                elif count == "all":
                    prize = random.randint(
                        VALENTINES_DAY_MIN_PRIZE * valentine,
                        VALENTINES_DAY_MAX_PRIZE * valentine
                    )
                    user.cash += prize
                    user.inventories[0].valentines -= valentine
                    await ctx.reply(f"{ctx.author.mention}, из валентинок выпало {prize} коинов! Поздравляем!")
                else:
                    prize = random.randint(VALENTINES_DAY_MIN_PRIZE * count, VALENTINES_DAY_MAX_PRIZE * count)
                    user.cash += prize
                    user.inventories[0].valentines -= count
                    await ctx.reply(f"{ctx.author.mention}, из валентинок выпало {prize} коинов! Поздравляем!")
