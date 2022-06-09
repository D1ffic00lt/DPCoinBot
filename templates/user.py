from __future__ import annotations

import io
import os
import discord
import requests

from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw

from .helperfunction import divide_the_number, create_emb, get_color, ignore_exceptions
from ..database.db import Database
from .json_ import Json
from .texts import *


class User(commands.Cog, name='user module', Database):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("server.db")
        self.bot: commands.Bot = bot
        self.name: discord.Member
        self.color: discord.Color
        self.all_cash: int
        self.level: int
        self.counter: int = 0
        self.index: int = 0
        self.ID: int = 0
        self.guild_id: int = 0

    @commands.command(aliases=['slb'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __slb(self, ctx: commands.context.Context):
        self.all_cash = 0
        self.color = get_color(ctx.author.roles)
        if not os.path.exists(".json/develop_get.json"):
            Json("develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json("develop_get.json").json_load()
        for row in self.get_from_user(ctx.guild.id, "Name", "Cash", "ID", order_by="Cash"):
            for member in ctx.guild.members:
                if str(member) == row[0]:
                    self.name = member
                    break
            if self.name is not None and not self.name.bot:
                for member in ctx.guild.members:
                    if self.name.id == member.id:
                        if self.name.id == 401555829620211723 and \
                                ctx.guild.id == 493970394374471680 and self.js["slb"] is False:
                            pass
                        else:
                            self.all_cash += row[1]
                        break
        await ctx.send(
            embed=create_emb(
                title="Общий баланс сервера:",
                color=self.color,
                args=[
                    {
                        "name": f"Баланс сервера {ctx.guild}",
                        "value": f"Общий баланс сервера {ctx.guild} составляет "
                                 f"{divide_the_number(self.all_cash)} "
                                 f" DP коинов",
                        "inline": False
                    }
                ]
            )
        )

    @commands.command(aliases=["leader", "lb"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __lb(self, ctx: commands.context.Context, type_: str = None):
        self.counter = 0
        self.name: discord.Member
        self.index = 0
        if not os.path.exists(".json/develop_get.json"):
            Json("develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json("develop_get.json").json_load()
        if type_ is None:
            self.emb = discord.Embed(title="Топ 10 сервера")
            for row in self.get_from_user(ctx.guild.id, "Name", "Cash", "Lvl", "ID", order_by="Cash"):
                if self.index == 10:
                    break
                for member in ctx.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in ctx.guild.members:
                        if member.id == row[3]:
                            if self.name.id == 401555829620211723 and ctx.guild.id == 493970394374471680 \
                                    and self.js["lb"] is False:
                                continue
                            else:
                                self.counter += 1
                                self.emb.add_field(
                                    name=f'# {self.counter} | `{row[0]}` | lvl `{row[2]}`',
                                    value=f'Баланс: {divide_the_number(row[1])}',
                                    inline=False
                                )
                                self.index += 1
                            break
                        else:
                            continue

            await ctx.send(embed=self.emb)
        elif type_ == "chat":
            self.emb = discord.Embed(title="Топ 10 сервера по левелу")
            for row in self.get_from_user(ctx.guild.id, "Name", "ChatLevel", "ID", "Xp", order_by="Xp"):
                if self.index == 10:
                    break
                for member in ctx.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in ctx.guild.members:
                        if member.id == row[2]:
                            self.counter += 1
                            self.emb.add_field(
                                name=f'# {self.counter} | `{row[0]}` | chat lvl `{row[1]}`',
                                value=f'xp: **{divide_the_number(row[3])}**',
                                inline=False
                            )
                            self.index += 1
                            break

            await ctx.send(embed=self.emb)
        elif type_ == "voice":
            self.emb = discord.Embed(title="Топ 10 сервера по времени в голосовых каналах")
            for row in self.get_from_user(
                    ctx.guild.id,
                    "Name",
                    "MinutesInVoiceChannels",
                    "ID",
                    order_by="MinutesInVoiceChannels"
            ):
                if self.index == 10:
                    break
                for member in ctx.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in ctx.guild.members:
                        if member.id == row[2]:
                            self.counter += 1
                            self.emb.add_field(
                                name=f'# {self.counter} | `{row[0]}`',
                                value=f'**{divide_the_number(row[1])} минут ({divide_the_number(row[1] / 60)} часов)**',
                                inline=False
                            )
                            self.index += 1
                            break

            await ctx.send(embed=self.emb)

    @ignore_exceptions  # т.к member может не быть на сервере, но упомянут через <@id>
    @commands.command(aliases=["balance", "cash"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __balance(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None
    ):
        if member is None:
            await ctx.send(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя `{ctx.author}` составляет "
                                f"`{divide_the_number(self.get_cash(ctx.author.id, ctx.guild.id))}` DP коинов"
                )
            )
        else:
            await ctx.send(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя `{member}` составляет "
                                f"`{divide_the_number(self.get_cash(member.id, ctx.guild.id))}` DP коинов"
                )
            )

    @commands.command(aliases=["bank"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __bank(
            self,
            ctx: commands.context.Context,
            action: str = None,
            cash: int | str = None
    ) -> None:
        if action is None:
            await ctx.send(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя `{ctx.author}` составляет "
                                f"`{divide_the_number(self.get_cash(ctx.author.id, ctx.guild.id))}` DP коинов\n\n"
                                f"Баланс в банке составляет"
                                f"`{divide_the_number(self.get_cash(ctx.author.id, ctx.guild.id, bank=True))}` "
                                f"DP коинов\n\nВсего коинов - `"
                                f"""{divide_the_number(
                                    self.get_cash(
                                        ctx.author.id,
                                        ctx.guild.id
                                    )
                                ) + divide_the_number(
                                    self.get_cash(
                                        ctx.author.id,
                                        ctx.guild.id,
                                        bank=True
                                    )
                                )}`"""
                )
            )
        elif action == "add":
            if await self.cash_check(ctx, cash):
                self.add_coins_to_the_bank(ctx.author.id, ctx.guild.id, cash)
                await ctx.message.add_reaction('✅')

        elif action == "take":
            if cash == "all":
                self.take_coins_from_the_bank(ctx.author.id, ctx.guild.id, "all")
            else:
                if cash is None:
                    await ctx.send(f"""{ctx.author.mention}, Вы не ввели сумму!""")
                elif cash > self.get_cash(ctx.author.id, ctx.guild.id, bank=True):
                    await ctx.send(f"""{ctx.author.mention}, у Вас недостаточно средств!""")
                if await self.cash_check(ctx, cash):
                    self.take_coins_from_the_bank(ctx.author.id, ctx.guild.id, cash)
                    await ctx.message.add_reaction('✅')

    @commands.command(aliases=['levels'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __levels_shop(self, ctx: commands.context.Context):
        await ctx.send(embed=create_emb(
            title="Всё о левелах!",
            args=[
                {
                    "name": f'Level 1',
                    "value": levels["level1"],
                    "inline": False
                },
                {
                    "name": f'Level 2',
                    "value": levels["level2"],
                    "inline": False
                },
                {
                    "name": f'Level 3',
                    "value": levels["level3"],
                    "inline": False
                },
                {
                    "name": f'Level 4',
                    "value": levels["level4"],
                    "inline": False
                },
                {
                    "name": f'Level 5',
                    "value": levels["level5"],
                    "inline": False
                },
                {
                    "name": f'**Как поднять левел?**',
                    "value": levels["LevelUp"],
                    "inline": False
                }
            ]
        )
        )

    @commands.command(aliases=['lvl_up'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __level_up(self, ctx: commands.context.Context):
        self.level = self.get_level(ctx.author.id, ctx.guild.id)
        if self.level == 5:
            await ctx.send("У Вас максимальный левел!")
        elif self.level == 1:
            if 50000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 50000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
        elif self.level == 2:
            if 100000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 100000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
        elif self.level == 3:
            if 200000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 200000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
        elif self.level == 4:
            if 400000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 400000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['shop'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __shop(self, ctx: commands.context.Context):
        self.emb = discord.Embed(title="Магазин ролей")
        for row in self.get_from_shop(ctx.guild.id, "RoleID", "RoleCost", order_by="RoleCost"):
            if ctx.guild.get_role(row[0]) is not None:
                self.emb.add_field(
                    name=f'Роль {ctx.guild.get_role(row[0]).mention}',
                    value=f'Стоимость: **{row[1]} DP коинов**',
                    inline=False
                )
        self.emb.add_field(name="**Как купить роль?**",
                           value=f'''```diff\n- {settings["prefix"]}buy <Упоминание роли>\n```''')
        self.get_from_item_shop(ctx.guild.id, "ItemID", "ItemName", "ItemCost", order_by="Cost")
        if self.get_from_item_shop(
                ctx.guild.id,
                "ItemID",
                "ItemName",
                "ItemCost",
                order_by="Cost"
        ).fetchone() is not None:
            self.emb.add_field(name='**Другое:**\n', value="Сообщение о покупке придет администрации!", inline=False)
            for row in self.get_from_item_shop(ctx.guild.id, "ItemID", "ItemName", "ItemCost", order_by="Cost"):
                self.emb.add_field(
                    name=f'**{row[1]}**',
                    value=f'Стоимость: **{row[2]} DP коинов**\n'
                          f'Чтобы купить {settings["prefix"]}buy_item {row[0]}',
                    inline=False
                )

        self.emb.add_field(
            name="**Чтобы купить роль:**",
            value=f"```diff\n- {settings['prefix']}buy @роль, которую Вы хотите купить\n```")
        await ctx.send(embed=self.emb)

    @commands.command(aliases=["buy_item"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy_item(self, ctx: commands.context.Context, item: int = None):
        if item is None:
            await ctx.send(f"""{ctx.author}, укажите то, что Вы хотите приобрести""")
        else:
            self.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="Cost")
            if self.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="Cost").fetchone() is None:
                await ctx.send(f"""{ctx.author}, такого товара не существует!""")
            elif self.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="Cost").fetchone()[0] > self.get_cash(
                    ctx.author.id, ctx.guild.id
            ):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.get_item_from_item_shop(ctx.guild.id, item, "Cost", order_by="Cost")
                )
                await ctx.message.add_reaction('✅')
                channel = self.bot.get_channel(self.get_from_server(ctx.guild.id, "ChannelID"))
                await channel.send(f"Покупка {ctx.author.mention} товар номер {item}")
                await ctx.send("Администрация скоро выдаст Вам товар")

    @commands.command(aliases=["buy", "buy-role"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy(self, ctx: commands.context.Context, role: discord.Role = None):
        if role is None:
            await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите приобрести""")
        else:
            if role in ctx.author.roles:
                await ctx.send(f"""{ctx.author}, у Вас уже есть эта роль!""")
            elif self.get_from_shop(ctx.author.id, ctx.guild.id, "Cost", order_by="Cost").fetchone() is None:
                pass
            elif self.get_from_shop(ctx.author.id, ctx.guild.id, "Cost", order_by="Cost").fetchone()[0] > self.get_cash(
                    ctx.author.id, ctx.guild.id
            ):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств для покупки этой роли!""")
            else:
                await ctx.author.add_roles(role)
                self.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.get_from_shop(
                        ctx.guild.id,
                        "RoleCost",
                        order_by="RoleCost",
                        role_id=role.id
                    )
                )
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["send"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None,
            cash: int = None
    ):
        if member is None:
            await ctx.send(f"""{ctx.author}, укажите пользователя, которому Вы хотите перевести коины""")
        else:
            if await self.cash_check(ctx, cash, check=True):
                if member.id == ctx.author.id:
                    await ctx.send(f"""{ctx.author}, Вы не можете перевести деньги себе""")
                else:
                    self.take_coins(ctx.author.id, ctx.guild.id, cash)
                    self.add_coins(member.id, ctx.guild.id, cash)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["+rep"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __good_rep(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None
    ):
        if member is None:
            await ctx.send(f"{ctx.author}, Вы не указали пользователя!")
        else:
            if member.id == ctx.author.id:
                await ctx.send(f"{ctx.author}, Вы не можете повысить репутацию самому себе")
            else:
                self.add_reputation(ctx.author.id, ctx.guild.id, 1)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["-rep"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __bad_rep(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None
    ):
        if member is None:
            await ctx.send(f"{ctx.author}, Вы не указали пользователя!")
        else:
            if member.id == ctx.author.id:
                await ctx.send(f"{ctx.author}, Вы не можете понизить репутацию самому себе")
            else:
                self.add_reputation(ctx.author.id, ctx.guild.id, -1)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["rep"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __rep(self, ctx):
        self.emb = discord.Embed(title="Топ 10 сервера")
        self.counter = 0
        for row in self.get_from_user(ctx.guild.id, "Name", "Reputation", order_by="Reputation", limit=10):
            self.counter += 1
            self.emb.add_field(
                name=f'# {self.counter} | `{row[0]}`',
                value=f'Репутация: {row[1]}',
                inline=False
            )
        await ctx.send(embed=self.emb)

    @commands.command(aliases=["stats"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __stats(self, ctx, member: discord.Member = None):
        self.ID = ctx.author.id if member is None else member.id
        self.guild_id = ctx.guild.id if member is None else member.guild.id
        await ctx.send(
            embed=create_emb(
                title="Статистика {}".format(ctx.author),
                args=[
                    {
                        "name": f'Coinflips - {self.get_stat(self.ID, self.guild_id, "CoinFlipsCount")}',
                        "value": f'Wins - {self.get_stat(self.ID, self.guild_id, "CoinFlipsCount")}\n '
                                 f'Loses - {self.get_stat(self.ID, self.guild_id, "CoinFlipsLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'Rust casinos - {self.get_stat(self.ID, self.guild_id, "RustCasinosCount")}',
                        "value": f'Wins - {self.get_stat(self.ID, self.guild_id, "RustCasinoWinsCount")}\n '
                                 f'Loses - {self.get_stat(self.ID, self.guild_id, "RustCasinoLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'Rolls - {self.get_stat(self.ID, self.guild_id, "RollsCount")}',
                        "value": f'Wins - {self.get_stat(self.ID, self.guild_id, "RollsWinsCount")}\n '
                                 f'Loses - {self.get_stat(self.ID, self.guild_id, "RollsLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'Fails - {self.get_stat(self.ID, self.guild_id, "FailsCount")}',
                        "value": f'Wins - {self.get_stat(self.ID, self.guild_id, "FailsWinsCount")}\n '
                                 f'Loses - {self.get_stat(self.ID, self.guild_id, "FailsLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'777s - {self.get_stat(self.ID, self.guild_id, "ThreeSevensCount")}',
                        "value": f'Wins - {self.get_stat(self.ID, self.guild_id, "ThreeSevensWinsCount")}\n '
                                 f'Loses - {self.get_stat(self.ID, self.guild_id, "ThreeSevensLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": 'Побед/Поражений всего',
                        "value": f'Wins - {self.get_stat(self.ID, self.guild_id, "AllWins")}\n '
                                 f'Loses - {self.get_stat(self.ID, self.guild_id, "AllLoses")}',
                        "inline": True
                    },
                    {
                        "name": 'Выиграно всего',
                        "value": divide_the_number(
                            self.get_stat(
                                self.ID,
                                self.guild_id,
                                "EntireAmountOfWinnings"
                            )
                        ),
                        "inline": True
                    },
                    {
                        "name": 'Минут в голосовых каналах',
                        "value": f'{self.get_stat(self.ID, self.guild_id, "MinutesInVoiceChannels")} минут',
                        "inline": True
                    },
                    {
                        "name": 'Сообщений в чате',
                        "value": f'{self.get_stat(self.ID, self.guild_id, "MessagesCount")} сообщений в чате',
                        "inline": True
                    },
                    {
                        "name": f'{self.get_stat(self.ID, self.guild_id, "ChatLevel")} левел в чате',
                        "value": '{} опыта до следующего левела, {} опыта всего',
                        "inline": True
                    }
                ]
            )
        )

    @commands.command(aliases=["card"])
    async def __Card(self, ctx):
        img = Image.new("RGBA", (500, 300), "#323642")
        Image.open(
            io.BytesIO(
                requests.get(
                    str(ctx.author.avatar_url)[:-10],
                    stream=True
                ).content
            )
        ).convert("RGBA").resize(
            (100, 100), Image.ANTIALIAS
        ).save(f"prom_files/avatar{ctx.author.id}.png")
        crop(
            Image.open(f'prom_files/avatar{ctx.author.id}.png'),
            (100, 100)
        ).putalpha(
            prepare_mask(
                (100, 100),
                4
            )
        ).save(f'prom_files/out_avatar{ctx.author.id}.png')

        img.alpha_composite(
            Image.open(
                f'prom_files/out_avatar{ctx.author.id}.png',
            ).convert("RGBA").resize(
                (100, 100), Image.ANTIALIAS
            ), (15, 15)
        )

        imagedraw = ImageDraw.Draw(img)
        wins = 0
        loses = 0
        vm = 0
        messages = 0

        for i in self.get_from_user(
                ctx.author.id, ctx.guild.id,
                "AllWins", "AllLoses", "MinutesInVoiceChannels", "MessagesCount",
                order_by="AllWins"
        ):
            wins += i[0]
            loses += i[1]
            vm += i[2]
            messages += i[3]

        imagedraw.text(
            (130, 15),
            f"{ctx.author.name}#{ctx.author.discriminator}",
            font=ImageFont.truetype('calibri.ttf', size=30)
        )
        imagedraw.text(
            (130, 45),
            f"ID: {ctx.author.id}",
            font=ImageFont.truetype("calibri.ttf", size=20)
        )
        imagedraw.text(
            (15, 125),
            f"Wins: {wins}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        imagedraw.text(
            (15, 160),
            f"Loses: {divide_the_number(loses)}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        imagedraw.text(
            (15, 195),
            f"Minutes in voice: {divide_the_number(vm)}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        imagedraw.text(
            (15, 230),
            f"Messages: {divide_the_number(messages)}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        images = []
        ver, dev, cod = cursor.execute("SELECT verification, developer, coder FROM card WHERE id = ?",
                                       [ctx.author.id]).fetchone()
        if int(ver) == 1:
            image = Image.open("progfiles/images/green_galka.png")
            image = image.convert("RGBA")
            image = image.resize((30, 30), Image.ANTIALIAS)
            images.append(image)
        elif int(ver) == 2:
            image = Image.open("progfiles/images/galka.png")
            image = image.convert("RGBA")
            image = image.resize((30, 30), Image.ANTIALIAS)
            images.append(image)
        if int(dev) == 1:
            image = Image.open("progfiles/images/developer.png")
            image = image.convert("RGBA")
            image = image.resize((30, 30), Image.ANTIALIAS)
            images.append(image)
        if int(cod) == 1:
            image = Image.open("progfiles/images/cmd.png")
            image = image.convert("RGBA")
            image = image.resize((30, 30), Image.ANTIALIAS)
            images.append(image)
        if len(images) != 0:
            x = 128
            for i in range(len(images)):
                img.alpha_composite(images[i], (x, 70))
                x += 35

        img.save(f'prom_files/user_card{ctx.author.id}.png')

        await ctx.send(file=discord.File(fp=f'prom_files/user_card{ctx.author.id}.png'))
        os.remove(f"prom_files/user_card{ctx.author.id}.png")
        os.remove(f"prom_files/avatar{ctx.author.id}.png")
        os.remove(f"prom_files/out_avatar{ctx.author.id}.png")
