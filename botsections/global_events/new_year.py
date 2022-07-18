import discord
import random

from datetime import datetime
from discord.ext import commands
from typing import Union
from dislash import slash_command, Option, OptionType

from botsections.database.db import Database
from botsections.texts import *


class NewYear(commands.Cog, name='NewYear module', Database):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("server.db")
        self.bot: commands.Bot = bot

    @commands.command(aliases=["use"])
    @slash_command(
        name="use", description="использовать предмет",
        options=[
            Option("item", "номер предмета, который вы хотите использовать", OptionType.INTEGER)
        ]
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __use(self, ctx: commands.context.Context, item: int = None) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                if item is None:
                    await ctx.send(f'{ctx.author.mention}, Вы не ввели предмет')
                else:
                    if item in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                        self.index = 0
                        for i in new_year:
                            if new_year[i]['index'] == item:
                                self.index = i
                                break
                        if self.get_from_new_year_event(ctx.author.id, ctx.guild.id, self.index) == 0:
                            await ctx.send(f"{ctx.author.mention}, у Вас нет этого:(")
                        else:
                            self.emb = discord.Embed(title=f"Использовано {new_year[self.index]['name']}!")
                            self.update_new_year_event(
                                ctx.author.id, ctx.guild.id,
                                "MoodCount", new_year[self.index]['mood']
                            )
                            self.emb.add_field(
                                name=f"Получено настроения",
                                value=f'Получено - {new_year[self.index]["mood"]}'
                            )
                            if random.randint(1, 101) >= new_year[self.index]['ylt_%']:
                                self.update_stat(ctx.author.id, ctx.guild.id, "Xp", new_year[self.index]['xp'])
                                self.emb.add_field(
                                    name=f"Получено опыта",
                                    value=f'Получено - {new_year[self.index]["xp"]}')
                                self.xp = self.get_stat(ctx.author.id, ctx.guild.id, "Xp")
                                self.level_in_chat = self.get_stat(ctx.author.id, ctx.guild.id, "ChatLevel")
                                for i in self.get_from_levels("XP", "Level", "Award"):
                                    if i[0] <= self.xp and i[1] > self.level_in_chat:
                                        self.update_stat(ctx.author.id, ctx.guild.id, "ChatLevel", 1)
                                        self.add_coins(ctx.author.id, ctx.guild.id, i[2])
                                        try:
                                            await ctx.author.send(
                                                f"{ctx.author.mention}, поздравляем с "
                                                f"{i[1]} левелом!\n"
                                                f"Вот тебе немного коинов! (**{i[2]}**)\n"
                                                f"Опыта для следующего левела - "
                                                f"**{self.get_xp(i[1] + 1) - self.xp}**, "
                                                f"{self.xp} опыта всего"
                                            )
                                        except discord.errors.Forbidden:
                                            pass
                                        break
                            self.update_new_year_event(ctx.author.id, ctx.guild.id, self.index, -1)
                            await ctx.send(embed=self.emb)

    @commands.command(aliases=["buy_food"])
    @slash_command(
        name="buy_food", description="купить еду",
        options=[
            Option("number", "номер предмета, который вы хотите использовать", OptionType.INTEGER),
            Option("count", "количество предметов, которых вы хотите купить", OptionType.INTEGER)
        ]
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __buy_food(self, ctx: commands.context.Context, number: int = 0, count: int = 1):
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                if not 10 > number >= 0:
                    await ctx.send(f"{ctx.author.mention}, аргумент не верен!")
                elif count <= 0:
                    await ctx.send("Вы не можете указать количество меньше 0!")
                elif count > 10:
                    await ctx.send("Вы не можете указать количество больше 10!")
                else:
                    for i in new_year:
                        if new_year[i]['index'] == int(number):
                            self.index = i
                            break
                    if (new_year[self.index]['price'] * count) > self.get_cash(ctx.author.id, ctx.guild.id):
                        await ctx.send(f"{ctx.author.mention}, у Вас недостаточно средств!")
                    else:
                        self.take_coins(ctx.author.id, ctx.guild.id, new_year[self.index]['price'] * count)
                        self.update_new_year_event(ctx.author.id, ctx.guild.id, self.index, count)
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["send_present"])
    @slash_command(
        name="send_present", description="отправить подарок",
        options=[
            Option("member", "пользователь", OptionType.USER),
            Option("count", "количество подарков", OptionType.INTEGER)
        ]
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send_present(self, ctx: commands.context.Context, member: discord.Member = None, amount: int = None):
        if member is None:
            await ctx.send(f"""{ctx.author.mention}, укажите пользователя, которому Вы хотите перевести коины""")
        else:
            if amount is None:
                await ctx.send(f"""{ctx.author.mention}, Вы не ввели сумму!""")
            elif amount > self.get_from_inventory(ctx.author.id, ctx.guild.id, "NewYearPrises"):
                await ctx.send(f"""{ctx.author.mention}, у Вас недостаточно подарков для перевода""")
            elif amount < 1:
                await ctx.send(f"""{ctx.author.mention}, Вы не можете ввести число меньше 1!""")
            else:
                if member.id == ctx.author.id:
                    await ctx.send(f"""{ctx.author}, Вы не можете перевести деньги себе""")
                else:
                    self.update_inventory(ctx.author.id, ctx.guild.id, "NewYearPrises", -amount)
                    self.update_inventory(member.id, member.guild.id, "NewYearPrises", amount)

                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["open"])
    @slash_command(
        name="open", description="открыть подарок",
        options=[
            Option("count", "количество подарков", Union[OptionType.INTEGER, OptionType.STRING])
        ]
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __open(self, ctx: commands.context.Context, count: Union[int, str] = None) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.present = self.get_from_inventory(ctx.author.id, ctx.guild.id, "NewYearPrises")
                if self.present == 0:
                    await ctx.send("У Вас нет подарков:(")
                    return
                if isinstance(count, int):
                    if int(count) > self.present:
                        await ctx.send("У Вас недостаточно подарков:(\nУ Вас {} подарков".format(self.present))
                        return
                    elif int(count) <= 0:
                        await ctx.send(f"{ctx.author.mention}, Вы не можете отрыть 0(ну или меньше) подарков:)")
                        return
                if count is None:
                    self.prize = random.randint(100, 3500)
                    self.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                    self.add_present(ctx.author.id, ctx.guild.id, -1)
                    await ctx.send(f"{ctx.author.mention}, из подарка выпало {self.prize} коинов! Поздравляем!")
                elif count == "all":
                    self.prize = sum(random.randint(100, 3500) for _ in range(self.present))
                    self.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                    await ctx.send(f"{ctx.author.mention}, из подарков выпало {self.prize} коинов! Поздравляем!")
                    self.add_present(ctx.author.id, ctx.guild.id, -self.present)
                else:
                    try:
                        self.prize = sum(random.randint(100, 3500) for _ in range(int(count)))
                        self.add_coins(ctx.author.id, ctx.guild.id, self.prize)
                        self.add_present(ctx.author.id, ctx.guild.id, -count)
                        await ctx.send(f"{ctx.author.mention}, из подарков выпало {self.prize} коинов! Поздравляем!")
                    except TypeError:
                        pass

    @commands.command(aliases=["presents"])
    @slash_command(
        name="presents", description="узнать количество подарков",
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __presents(self, ctx: commands.context.Context) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                await ctx.send(
                    f"{ctx.author.mention}\n```У Вас "
                    f"{self.get_from_inventory(ctx.author.id, ctx.guild.id, 'NewYearPrises')} подарков```"
                )

    @commands.command(aliases=["foodshop"])
    @slash_command(
        name="foodshop", description="магазин еды",
    )
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
                await ctx.send(embed=self.emb)

    @commands.command(aliases=["food"])
    @slash_command(
        name="food", description="Ваша еда",
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __food_e(self, ctx: commands.context.Context) -> None:
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if self.month > 11 or self.month == 1:
            if (self.month == 12 and self.day > 10) or (self.month == 1 and self.day < 15):
                self.emb = discord.Embed(title=f"Еда {ctx.author}")
                self.emb.set_thumbnail(url=ctx.author.avatar_url)
                self.index2 = 3
                self.items = tuple(self.get_from_new_year_event(ctx.author.id, ctx.guild.id, "*"))
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
                await ctx.send(embed=self.emb)
