import discord
import random

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from typing import Union

from database.db import Database
from botsections.functions.texts import *
from botsections.functions.additions import get_time, write_log
from botsections.functions.config import settings

__all__ = (
    "NewYearSlash",
)


class NewYearSlash(commands.Cog):
    NAME = 'NewYear slash module'

    __slots__ = (
        "bot", "db", "month", "day",
        "index", "index2", "emb", "xp",
        "level_in_chat", "items"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.emb: discord.Embed
        self.month: int = 0
        self.day: int = 0
        self.index: int = 0
        self.index2: int = 0
        self.prize: int = 0
        self.present: int = 0
        self.items: tuple = ()
        self.xp: Union[int, float] = 0
        self.level_in_chat: Union[int, float] = 0

        print(f"[{get_time()}] [INFO]: NewYearSlash event connected")
        write_log(f"[{get_time()}] [INFO]: NewYearSlash event connected")

    @app_commands.command(name="use")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __use(self, inter: discord.Interaction, item: int) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                if item is None:
                    await inter.response.send_message(
                        f'{inter.user.mention}, Вы не ввели предмет!', ephemeral=True
                    )
                else:
                    if item in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                        self.index = 0
                        for i in new_year:
                            if new_year[i]['index'] == item:
                                self.index = i
                                break
                        if self.db.get_from_new_year_event(inter.user.id, inter.guild.id, self.index) == 0:
                            await inter.response.send_message(
                                f"{inter.user.mention}, у Вас нет этого:(", ephemeral=True
                            )
                        else:
                            self.emb = discord.Embed(title=f"Использовано {new_year[self.index]['name']}!")
                            self.db.update_new_year_event(
                                inter.user.id, inter.guild.id,
                                "MoodCount", new_year[self.index]['mood']
                            )
                            self.emb.add_field(
                                name=f"Получено настроения",
                                value=f'Получено - {new_year[self.index]["mood"]}'
                            )
                            if random.randint(1, 101) >= new_year[self.index]['ylt_%']:
                                self.db.update_stat(inter.user.id, inter.guild.id, "Xp", new_year[self.index]['xp'])
                                self.emb.add_field(
                                    name=f"Получено опыта",
                                    value=f'Получено - {new_year[self.index]["xp"]}')
                                self.xp = self.db.get_stat(inter.user.id, inter.guild.id, "Xp")
                                self.level_in_chat = self.db.get_stat(inter.user.id, inter.guild.id, "ChatLevel")
                                for i in self.db.get_from_levels("XP", "Level", "Award"):
                                    if i[0] <= self.xp and i[1] > self.level_in_chat:
                                        self.db.update_stat(inter.user.id, inter.guild.id, "ChatLevel", 1)
                                        self.db.add_coins(inter.user.id, inter.guild.id, i[2])
                                        try:
                                            await inter.user.send(
                                                f"{inter.user.mention}, поздравляем с "
                                                f"{i[1]} левелом!\n"
                                                f"Вот тебе немного коинов! (**{i[2]}**)\n"
                                                f"Опыта для следующего левела - "
                                                f"**{self.db.get_xp(i[1] + 1) - self.xp}**, "
                                                f"{self.xp} опыта всего"
                                            )
                                        except discord.errors.Forbidden:
                                            pass
                                        break
                            self.db.update_new_year_event(inter.user.id, inter.guild.id, self.index, -1)
                            await inter.response.send_message(embed=self.emb)

    @app_commands.command(name="buy_food")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __buy_food(self, inter: discord.Interaction, number: int = 0, count: int = 1):
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                if not 10 > number >= 0:
                    await inter.response.send_message(f"{inter.user.mention}, аргумент не верен!", ephemeral=True)
                elif count <= 0:
                    await inter.response.send_message("Вы не можете указать количество меньше 0!", ephemeral=True)
                elif count > 10:
                    await inter.response.send_message("Вы не можете указать количество больше 10!", ephemeral=True)
                else:
                    for i in new_year:
                        if new_year[i]['index'] == int(number):
                            self.index = i
                            break
                    if (new_year[self.index]['price'] * count) > self.db.get_cash(inter.user.id, inter.guild.id):
                        await inter.response.send_message(
                            f"{inter.user.mention}, у Вас недостаточно средств!", ephemeral=True
                        )
                    else:
                        self.db.take_coins(inter.user.id, inter.guild.id, new_year[self.index]['price'] * count)
                        self.db.update_new_year_event(inter.user.id, inter.guild.id, self.index, count)
                        await inter.response.send_message('✅')

    @app_commands.command(name="send_present")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send_present(self, inter: discord.Interaction, member: discord.Member, amount: int):
        if member is None:
            await inter.response.send_message(
                f"{inter.user.mention}, укажите пользователя, которому Вы хотите перевести коины", ephemeral=True
            )
        else:
            if amount is None:
                await inter.response.send_message(
                    f"""{inter.user.mention}, Вы не ввели сумму!""", ephemeral=True
                )
            elif amount > self.db.get_from_inventory(inter.user.id, inter.guild.id, "NewYearPrises"):
                await inter.response.send_message(
                    f"""{inter.user.mention}, у Вас недостаточно подарков для перевода""", ephemeral=True
                )
            elif amount < 1:
                await inter.response.send_message(
                    f"""{inter.user.mention}, Вы не можете ввести число меньше 1!""", ephemeral=True
                )
            else:
                if member.id == inter.user.id:
                    await inter.response.send_message(
                        f"""{inter.user}, Вы не можете перевести деньги себе""", ephemeral=True
                    )
                else:
                    self.db.update_inventory(inter.user.id, inter.guild.id, "NewYearPrises", -amount)
                    self.db.update_inventory(member.id, member.guild.id, "NewYearPrises", amount)

                await inter.response.send_message('✅')

    @app_commands.command(name="open")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __open(self, inter: discord.Interaction, count: int = None) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.present = self.db.get_from_inventory(inter.user.id, inter.guild.id, "NewYearPrises")
                if self.present == 0:
                    await inter.response.send_message("У Вас нет подарков:(", ephemeral=True)
                    return
                if isinstance(count, int):
                    if int(count) > self.present:
                        await inter.response.send_message(
                            "У Вас недостаточно подарков:(\nУ Вас {} подарков".format(self.present), ephemeral=True
                        )
                        return
                    elif int(count) <= 0:
                        await inter.response.send_message(
                            f"{inter.user.mention}, Вы не можете отрыть 0(ну или меньше) подарков:)", ephemeral=True
                        )
                        return
                if count is None:
                    self.prize = random.randint(100, 3500)
                    self.db.add_coins(inter.user.id, inter.guild.id, self.prize)
                    self.db.take_present(1, inter.user.id, inter.guild.id)
                    await inter.response.send_message(
                        f"{inter.user.mention}, из подарка выпало {self.prize} коинов! Поздравляем!"
                    )
                elif count == "all":
                    self.prize = sum(random.randint(100, 3500) for _ in range(self.present))
                    self.db.add_coins(inter.user.id, inter.guild.id, self.prize)
                    await inter.response.send_message(
                        f"{inter.user.mention}, из подарков выпало {self.prize} коинов! Поздравляем!"
                    )
                    self.db.take_present(self.present, inter.user.id, inter.guild.id)
                else:
                    try:
                        self.prize = sum(random.randint(100, 3500) for _ in range(int(count)))
                        self.db.add_coins(inter.user.id, inter.guild.id, self.prize)
                        self.db.take_present(count, inter.user.id, inter.guild.id)
                        await inter.response.send_message(
                            f"{inter.user.mention}, из подарков выпало {self.prize} коинов! Поздравляем!"
                        )
                    except TypeError:
                        pass

    @app_commands.command(name="presents")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __presents(self, inter: discord.Interaction) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                await inter.response.send_message(
                    f"{inter.user.mention}\n```У Вас "
                    f"{self.db.get_from_inventory(inter.user.id, inter.guild.id, 'NewYearPrises')} подарков```"
                )

    @app_commands.command(name="foodshop")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __nwp(self, inter: discord.Interaction) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.emb = discord.Embed(title="Магазин Еды!")
                for i in new_year:
                    self.emb.add_field(
                        name=f"{new_year[i]['name']} ({new_year[i]['index']})",
                        value=f'{new_year[i]["price"]} DP коинов\n')
                self.emb.add_field(
                    name="Покупка еды",
                    value=f'Чтобы купить - {settings["prefix"]}buyfood <индекс товара>'
                          f'<количество>')
                await inter.response.send_message(embed=self.emb)

    @app_commands.command(name="food")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __food_e(self, inter: discord.Interaction) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.emb = discord.Embed(title=f"Еда {inter.user}")
                self.emb.set_thumbnail(url=inter.user.avatar_url)
                self.index2 = 3
                self.items = tuple(self.db.get_from_new_year_event(inter.user.id, inter.guild.id, "*"))
                for t in range(len(self.items) - 3):
                    if self.items[self.index2] != 0:
                        for j in new_year:
                            if (new_year[j]["index"] + 3) == self.index2:
                                self.emb.add_field(
                                    name=f"{new_year[j]['name']}",
                                    value=f'Количество - {self.items[self.index2]}\n'
                                          f'({j} или {new_year[j]["index"]})')
                    self.index2 += 1
                self.emb.add_field(
                    name=f"Настроение",
                    value=f'{self.items[-1]}')
                await inter.response.send_message(embed=self.emb)
