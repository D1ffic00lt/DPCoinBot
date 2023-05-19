# -*- coding: utf-8 -*-
import logging
import discord
import random

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from typing import Callable

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
    "NewYearSlash",
)


class NewYearSlash(commands.Cog):
    NAME = 'NewYear slash module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.session: Callable[[], AsyncSession] = session

        logging.info(f"NewYear (Slash) event connected")

    @app_commands.command(name="use", description="Использовать предмет")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __use(self, inter: discord.Interaction, item: int) -> None:
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if not month > 11 or month == 1:
            return
        if not (month == 12 and day > 10) or (month == 1 and day < 15):
            return
        if item is None:
            await inter.response.send_message(f'{inter.user.mention}, Вы не ввели предмет')
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
                        User.user_id == inter.user.id and User.guild_id == inter.guild.id
                    )
                )
                if not user:
                    return
                if user.new_year_events[0][index] == 0:
                    await inter.response.send_message(f"{inter.user.mention}, у Вас нет этого:(")
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
                await inter.response.send_message(embed=emb)

    @app_commands.command(name="buy_food", description="Купить еду")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __buy_food(self, inter: discord.Interaction, number: int = 0, count: int = 1):
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if month > 11 or month == 1:
            return
        if (month == 12 and day > 10) or (month == 1 and day < 15):
            return
        if not 10 > number >= 0:
            await inter.response.send_message(f"{inter.user.mention}, аргумент не верен!")
            return
        if count <= 0:
            await inter.response.send_message("Вы не можете указать количество меньше 0!")
            return
        if count > 10:
            await inter.response.send_message("Вы не можете указать количество больше 10!")
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
                        User.user_id == inter.user.id and User.guild_id == inter.guild.id
                    )
                )
                user: User | None = user.scalars().first()
                if not user:
                    return
                if (new_year[index]['price'] * count) > user.cash:
                    await inter.response.send_message(f"{inter.user.mention}, у Вас недостаточно средств!")
                    return
                user.cash -= new_year[index]['price'] * count
                user.new_year_events[0].update(index, count)
                await inter.response.send_message('✅')

    @app_commands.command(name="send_present", description="Отправить подарок!")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send_present(self, inter: discord.Interaction, member: discord.Member, amount: int):
        if member is None:
            await inter.response.send_message(
                f"""{inter.user.mention}, укажите пользователя, которому Вы хотите отправить подарки"""
            )
            return
        if amount is None:
            await inter.response.send_message(f"""{inter.user.mention}, Вы не ввели сумму!""")
            return
        async with self.session() as session:
            async with session.begin():
                sender = await session.execute(
                    select(User).where(
                        User.user_id == inter.user.id and User.guild_id == inter.guild.id
                    )
                )
                sender: None | User = sender.scalars().first()
                recipient = await session.execute(
                    select(User).where(
                        User.user_id == member.id and User.guild_id == inter.guild.id
                    )
                )
                recipient: None | User = recipient.scalars().first()
                if not recipient or not sender:
                    return
                if amount > sender.inventories[0].new_year_prises:
                    await inter.response.send_message(
                        f"""{inter.user.mention}, у Вас недостаточно подарков для перевода"""
                    )
                    return
                if amount < 1:
                    await inter.response.send_message(f"""{inter.user.mention}, Вы не можете ввести число меньше 1!""")
                    return
                if member.id == inter.user.id:
                    await inter.response.send_message(f"""{inter.user.mention}, Вы не можете перевести подарки себе""")
                sender.inventories[0].new_year_prises -= amount
                recipient.inventories[0].new_year_prises += amount

                await inter.response.send_message('✅')

    @app_commands.command(name="open", description="Открыть подарок")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __open(self, inter: discord.Interaction, count: int = None) -> None:
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
                        User.user_id == inter.user.id and User.guild_id == inter.guild.id
                    )
                )
                user: User | None = user.scalars().first()
                if not user:
                    return
                presents = user.inventories[0].new_year_prises
                if presents == 0:
                    await inter.response.send_message("У Вас нет подарков:(")
                    return
                if isinstance(count, int):
                    if int(count) > presents:
                        await inter.response.send_message(
                            "У Вас недостаточно подарков:(\nУ Вас {} подарков".format(presents)
                        )
                        return
                    elif int(count) <= 0:
                        await inter.response.send_message(f"Вы не можете отрыть 0(ну или меньше) подарков:)")
                        return
                if count is None:
                    prize = random.randint(NEW_YEAR_MIN_PRIZE, NEW_YEAR_MAX_PRIZE)
                    user.cash += prize
                    user.inventories[0].new_year_prises -= 1
                    await inter.response.send_message(f"Из подарка выпало {prize} коинов! Поздравляем!")
                    return
                elif count == "all":
                    prize = random.randint(NEW_YEAR_MIN_PRIZE * presents, NEW_YEAR_MAX_PRIZE * presents)
                    user.cash += prize
                    user.inventories[0].new_year_prises -= presents
                    await inter.response.send_message(f"Из подарков выпало {prize} коинов! Поздравляем!")
                    return
                try:
                    prize = random.randint(NEW_YEAR_MIN_PRIZE * int(count), NEW_YEAR_MAX_PRIZE * int(count))
                    user.cash += prize
                    user.inventories[0].new_year_prises -= count
                    await inter.response.send_message(f"Из подарков выпало {prize} коинов! Поздравляем!")
                except TypeError:
                    pass

    @app_commands.command(name="presents", description="Количество подарков")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __presents(self, inter: discord.Interaction) -> None:
        month = int(datetime.today().strftime('%m'))
        day = int(datetime.today().strftime('%d'))
        if month > 11 or month == 1:
            if (month == 12 and day > 10) or (month == 1 and day < 15):
                async with self.session() as session:
                    async with session.begin():
                        inventory = await session.execute(
                            select(Inventory).where(
                                Inventory.user_id == inter.user.id and Inventory.guild_id == inter.guild.id
                            )
                        )
                        inventory: Inventory | None = inventory.scalars().first()
                        if not inventory:
                            return
                        await inter.response.send_message(
                            f"{inter.user.mention}\n```У Вас "
                            f"{inventory.new_year_prises} подарков```"
                        )

    @app_commands.command(name="foodshop", description="Магазин новогодней еды")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __nwp(self, inter: discord.Interaction) -> None:
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
                await inter.response.send_message(embed=emb)
