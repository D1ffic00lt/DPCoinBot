# -*- coding: utf-8 -*-
""" TODO: /food """
import logging
import discord
import random

from datetime import datetime
from discord.ext import commands
from typing import Union, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.user.inventories import Inventory
from database.user.users import User
from units.texts import *
from config import (
    PREFIX,
    NEW_YEAR_MIN_PRIZE,
    NEW_YEAR_MAX_PRIZE
)

__all__ = (
    "NewYear",
)


class NewYear(commands.Cog):
    NAME = 'NewYear module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.session: Callable[[], AsyncSession] = session
        logging.info(f"NewYear event connected")

    @commands.command(aliases=["use"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __use(self, ctx: commands.context.Context, item: int = None) -> None:
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if not month > 11 or month == 1:
            return
        if not (month == 12 and day > 10) or (month == 1 and day < 15):
            return
        if item is None:
            await ctx.reply(f'{ctx.author.mention}, Вы не ввели предмет')
            return
        if item not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            return

        index = 0
        for i in new_year:
            if new_year[i]['index'] == item:
                index = i
                break
        async with self.session() as session:
            async with session.begin():
                user: User | None = session.execute(
                    select(User).where(
                        User.user_id == ctx.author.id and User.guild_id == ctx.guild.id
                    )
                )
                if not user:
                    return
                if user.new_year_events[0][index] == 0:
                    await ctx.reply(f"{ctx.author.mention}, у Вас нет этого:(")
                    return
                emb = discord.Embed(title=f"Использовано {new_year[index]['name']}!")
                user.new_year_events[0].mood_count = new_year[index]['mood']
                emb.add_field(
                    name=f"Получено настроения",
                    value=f'Получено - {new_year[index]["mood"]}'
                )
                if random.randint(1, 101) >= new_year[index]['ylt_%']:
                    user.users_stats[0].xp += new_year[index]['xp']
                    emb.add_field(
                        name=f"Получено опыта",
                        value=f'Получено - {new_year[index]["xp"]}')
                user.new_year_events[0].update(index, -1)
                await ctx.reply(embed=emb)

    @commands.command(aliases=["buy_food"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __buy_food(self, ctx: commands.context.Context, number: int = 0, count: int = 1):
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if month > 11 or month == 1:
            return
        if (month == 12 and day > 10) or (month == 1 and day < 15):
            return
        if not 10 > number >= 0:
            await ctx.reply(f"{ctx.author.mention}, аргумент не верен!")
            return
        if count <= 0:
            await ctx.reply("Вы не можете указать количество меньше 0!")
            return
        if count > 10:
            await ctx.reply("Вы не можете указать количество больше 10!")
            return
        index = 0
        for i in new_year:
            if new_year[i]['index'] == int(number):
                index = i
                break
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
                if (new_year[index]['price'] * count) > user.cash:
                    await ctx.reply(f"{ctx.author.mention}, у Вас недостаточно средств!")
                    return
                user.cash -= new_year[index]['price'] * count
                user.new_year_events[0].update(index, count)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["send_present"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send_present(self, ctx: commands.context.Context, member: discord.Member = None, amount: int = None):
        if member is None:
            await ctx.reply(f"""{ctx.author.mention}, укажите пользователя, которому Вы хотите отправить подарки""")
            return
        if amount is None:
            await ctx.reply(f"""{ctx.author.mention}, Вы не ввели сумму!""")
            return
        async with self.session() as session:
            async with session.begin():
                sender = await session.execute(
                    select(User).where(
                        User.user_id == ctx.author.id and User.guild_id == ctx.guild.id
                    )
                )
                sender: None | User = sender.scalars().first()
                recipient = await session.execute(
                    select(User).where(
                        User.user_id == member.id and User.guild_id == ctx.guild.id
                    )
                )
                recipient: None | User = recipient.scalars().first()
                if not recipient or not sender:
                    return
                if amount > sender.inventories[0].new_year_prises:
                    await ctx.reply(f"""{ctx.author.mention}, у Вас недостаточно подарков для перевода""")
                    return
                if amount < 1:
                    await ctx.reply(f"""{ctx.author.mention}, Вы не можете ввести число меньше 1!""")
                    return
                if member.id == ctx.author.id:
                    await ctx.reply(f"""{ctx.author}, Вы не можете перевести подарки себе""")
                sender.inventories[0].new_year_prises -= amount
                recipient.inventories[0].new_year_prises += amount

                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["open"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __open(self, ctx: commands.context.Context, count: Union[int, str] = None) -> None:
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if month > 11 or month == 1:
            return
        if (month == 12 and day > 10) or (month == 1 and day < 15):
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
                presents = user.inventories[0].new_year_prises
                if presents == 0:
                    await ctx.reply("У Вас нет подарков:(")
                    return
                if isinstance(count, int):
                    if int(count) > presents:
                        await ctx.reply("У Вас недостаточно подарков:(\nУ Вас {} подарков".format(presents))
                        return
                    elif int(count) <= 0:
                        await ctx.reply(f"Вы не можете отрыть 0(ну или меньше) подарков:)")
                        return
                if count is None:
                    prize = random.randint(NEW_YEAR_MIN_PRIZE, NEW_YEAR_MAX_PRIZE)
                    user.cash += prize
                    user.inventories[0].new_year_prises -= 1
                    await ctx.reply(f"Из подарка выпало {prize} коинов! Поздравляем!")
                    return
                elif count == "all":
                    prize = random.randint(NEW_YEAR_MIN_PRIZE * presents, NEW_YEAR_MAX_PRIZE * presents)
                    user.cash += prize
                    user.inventories[0].new_year_prises -= presents
                    await ctx.reply(f"Из подарков выпало {prize} коинов! Поздравляем!")
                    return
                try:
                    prize = random.randint(NEW_YEAR_MIN_PRIZE * int(count), NEW_YEAR_MAX_PRIZE * int(count))
                    user.cash += prize
                    user.inventories[0].new_year_prises -= count
                    await ctx.reply(f"Из подарков выпало {prize} коинов! Поздравляем!")
                except TypeError:
                    pass

    @commands.command(aliases=["presents"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __presents(self, ctx: commands.context.Context) -> None:
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if month > 11 or month == 1:
            if (month == 12 and day > 10) or (month == 1 and day < 15):
                async with self.session() as session:
                    async with session.begin():
                        inventory = await session.execute(
                            select(Inventory).where(
                                Inventory.user_id == ctx.author.id and Inventory.guild_id == ctx.guild.id
                            )
                        )
                        inventory: Inventory | None = inventory.scalars().first()
                        if not inventory:
                            return
                        await ctx.reply(
                            f"{ctx.author.mention}\n```У Вас "
                            f"{inventory.new_year_prises} подарков```"
                        )

    @commands.command(aliases=["foodshop"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __nwp(self, ctx: commands.context.Context) -> None:
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if month > 11 or month == 1:
            if (month == 12 and day > 10) or (month == 1 and day < 15):
                emb = discord.Embed(title="Магазин Еды!")
                for i in new_year:
                    emb.add_field(
                        name=f"{new_year[i]['name']} ({new_year[i]['index']})",
                        value=f'{new_year[i]["price"]} DP коинов\n')
                emb.add_field(
                    name="Покупка еды",
                    value=f'Чтобы купить - {PREFIX}buyfood <индекс товара>'
                          f'<количество>')
                await ctx.reply(embed=emb)
