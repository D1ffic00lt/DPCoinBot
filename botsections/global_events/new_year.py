import discord
import random

from datetime import datetime
from discord.ext import commands
from typing import Union

from database.db import Database
from botsections.functions.texts import *
from botsections.functions.additions import get_time, write_log
from botsections.functions.config import settings

__all__ = (
    "NewYear",
)


class NewYear(commands.Cog):
    NAME = 'NewYear module'

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
        print(f"[{get_time()}] [INFO]: NewYear event connected")
        write_log(f"[{get_time()}] [INFO]: NewYear event connected")

    @commands.command(aliases=["use"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __use(self, ctx: commands.context.Context, item: int = None) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                if item is None:
                    await ctx.reply(f'{ctx.author.mention}, Вы не ввели предмет')
                else:
                    if item in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                        self.index = 0
                        for i in new_year:
                            if new_year[i]['index'] == item:
                                self.index = i
                                break
                        if self.db.get_from_new_year_event(ctx.author.id, ctx.guild.id, self.index) == 0:
                            await ctx.reply(f"{ctx.author.mention}, у Вас нет этого:(")
                        else:
                            self.emb = discord.Embed(title=f"Использовано {new_year[self.index]['name']}!")
                            self.db.update_new_year_event(
                                ctx.author.id, ctx.guild.id,
                                "MoodCount", new_year[self.index]['mood']
                            )
                            self.emb.add_field(
                                name=f"Получено настроения",
                                value=f'Получено - {new_year[self.index]["mood"]}'
                            )
                            if random.randint(1, 101) >= new_year[self.index]['ylt_%']:
                                self.db.update_stat(ctx.author.id, ctx.guild.id, "Xp", new_year[self.index]['xp'])
                                self.emb.add_field(
                                    name=f"Получено опыта",
                                    value=f'Получено - {new_year[self.index]["xp"]}')
                                self.xp = self.db.get_stat(ctx.author.id, ctx.guild.id, "Xp")
                                self.level_in_chat = self.db.get_stat(ctx.author.id, ctx.guild.id, "ChatLevel")
                                for i in self.db.get_from_levels("XP", "Level", "Award"):
                                    if i[0] <= self.xp and i[1] > self.level_in_chat:
                                        self.db.update_stat(ctx.author.id, ctx.guild.id, "ChatLevel", 1)
                                        self.db.add_coins(ctx.author.id, ctx.guild.id, i[2])
                                        try:
                                            await ctx.author.send(
                                                f"{ctx.author.mention}, поздравляем с "
                                                f"{i[1]} левелом!\n"
                                                f"Вот тебе немного коинов! (**{i[2]}**)\n"
                                                f"Опыта для следующего левела - "
                                                f"**{self.db.get_xp(i[1] + 1) - self.xp}**, "
                                                f"{self.xp} опыта всего"
                                            )
                                        except discord.errors.Forbidden:
                                            pass
                                        break
                            self.db.update_new_year_event(ctx.author.id, ctx.guild.id, self.index, -1)
                            await ctx.reply(embed=self.emb)

    @commands.command(aliases=["buy_food"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __buy_food(self, ctx: commands.context.Context, number: int = 0, count: int = 1):
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                if not 10 > number >= 0:
                    await ctx.reply(f"{ctx.author.mention}, аргумент не верен!")
                elif count <= 0:
                    await ctx.reply("Вы не можете указать количество меньше 0!")
                elif count > 10:
                    await ctx.reply("Вы не можете указать количество больше 10!")
                else:
                    for i in new_year:
                        if new_year[i]['index'] == int(number):
                            self.index = i
                            break
                    if (new_year[self.index]['price'] * count) > self.db.get_cash(ctx.author.id, ctx.guild.id):
                        await ctx.reply(f"{ctx.author.mention}, у Вас недостаточно средств!")
                    else:
                        self.db.take_coins(ctx.author.id, ctx.guild.id, new_year[self.index]['price'] * count)
                        self.db.update_new_year_event(ctx.author.id, ctx.guild.id, self.index, count)
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["send_present"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send_present(self, ctx: commands.context.Context, member: discord.Member = None, amount: int = None):
        if member is None:
            await ctx.reply(f"""{ctx.author.mention}, укажите пользователя, которому Вы хотите перевести коины""")
        else:
            if amount is None:
                await ctx.reply(f"""{ctx.author.mention}, Вы не ввели сумму!""")
            elif amount > self.db.get_from_inventory(ctx.author.id, ctx.guild.id, "NewYearPrises"):
                await ctx.reply(f"""{ctx.author.mention}, у Вас недостаточно подарков для перевода""")
            elif amount < 1:
                await ctx.reply(f"""{ctx.author.mention}, Вы не можете ввести число меньше 1!""")
            else:
                if member.id == ctx.author.id:
                    await ctx.reply(f"""{ctx.author}, Вы не можете перевести деньги себе""")
                else:
                    self.db.update_inventory(ctx.author.id, ctx.guild.id, "NewYearPrises", -amount)
                    self.db.update_inventory(member.id, member.guild.id, "NewYearPrises", amount)

                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["open"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __open(self, ctx: commands.context.Context, count: Union[int, str] = None) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.present = self.db.get_from_inventory(ctx.author.id, ctx.guild.id, "NewYearPrises")
                if self.present == 0:
                    await ctx.reply("У Вас нет подарков:(")
                    return
                if isinstance(count, int):
                    if int(count) > self.present:
                        await ctx.reply("У Вас недостаточно подарков:(\nУ Вас {} подарков".format(self.present))
                        return
                    elif int(count) <= 0:
                        await ctx.reply(f"Вы не можете отрыть 0(ну или меньше) подарков:)")
                        return
                if count is None:
                    self.prize = random.randint(100, 1000)
                    self.db.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                    self.db.take_present(1, ctx.author.id, ctx.guild.id)
                    await ctx.reply(f"Из подарка выпало {self.prize} коинов! Поздравляем!")
                elif count == "all":
                    self.prize = sum(random.randint(100, 1000) for _ in range(self.present))
                    self.db.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                    self.db.take_present(self.present, ctx.author.id, ctx.guild.id)
                    await ctx.reply(f"Из подарков выпало {self.prize} коинов! Поздравляем!")
                else:
                    try:
                        self.prize = sum(random.randint(100, 1000) for _ in range(int(count)))
                        self.db.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                        self.db.take_present(count, ctx.author.id, ctx.guild.id)
                        await ctx.reply(f"Из подарков выпало {self.prize} коинов! Поздравляем!")
                    except TypeError:
                        pass

    @commands.command(aliases=["presents"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __presents(self, ctx: commands.context.Context) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                await ctx.reply(
                    f"{ctx.author.mention}\n```У Вас "
                    f"{self.db.get_from_inventory(ctx.author.id, ctx.guild.id, 'NewYearPrises')} подарков```"
                )

    @commands.command(aliases=["foodshop"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __nwp(self, ctx: commands.context.Context) -> None:
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
                await ctx.reply(embed=self.emb)

    @commands.command(aliases=["food"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __food_e(self, ctx: commands.context.Context) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.emb = discord.Embed(title=f"Еда {ctx.author}")
                self.emb.set_thumbnail(url=ctx.author.avatar_url)
                self.index2 = 3
                self.items = tuple(self.db.get_from_new_year_event(ctx.author.id, ctx.guild.id, "*"))
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
                await ctx.reply(embed=self.emb)
