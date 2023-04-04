# -*- coding: utf-8 -*-
import io
import os
import discord
import requests
import logging

from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw
from typing import Union

from modules.additions import (
    divide_the_number, create_emb,
    get_color, prepare_mask, crop,
    get_promo_code
)
from modules.json_logging import Json
from config import PREFIX
from database.db import Database
from units.gpt.gpt3 import GTP3Model

__all__ = (
    "User",
)


class User(commands.Cog):
    NAME = 'user module'

    __slots__ = (
        "db", "bot", "name", "color", "all_cash",
        "level", "counter", "index", "ID",
        "guild_id", "server", "js",
        "emb", "img", "image_draw", "wins",
        "loses", "minutes_id_voice", "messages", "cash",
        "code", "code2", "response", "avatar", "gpt_users"
    )

    def __init__(self, bot: commands.Bot, db: Database, gpt_token: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.gpt_token = gpt_token
        self.server: Union[discord.Guild, type(None)]
        self.bot: commands.Bot = bot
        self.name: discord.Member
        self.color: discord.Color
        self.emb: discord.Embed
        self.img: Image
        self.image_draw: ImageDraw
        self.all_cash: int
        self.level: int
        self.counter: int = 0
        self.index: int = 0
        self.ID: int = 0
        self.guild_id: int = 0
        self.wins: int = 0
        self.loses: int = 0
        self.minutes_in_voice: int = 0
        self.lvl: int = 0
        self.all_xp: int = 0
        self.xp: int = 0
        self.messages: int = 0
        self.cash: int = 0
        self.code: str = ""
        self.code2: str = ""
        self.js: dict = {}
        self.gpt_users: dict[int, GTP3Model] = {}
        logging.info(f"User connected")

    @commands.command(aliases=["slb"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __slb(self, ctx: commands.context.Context) -> None:
        self.all_cash = 0
        self.color = get_color(ctx.author.roles)
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json(".json/develop_get.json").json_load()
        for row in self.db.get_from_user(ctx.guild.id, "Name", "Cash", "ID", order_by="Cash"):
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
        await ctx.reply(
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
    async def __lb(self, ctx: commands.context.Context, type_: str = None) -> None:
        self.counter = 0
        self.name: discord.Member
        self.index = 0
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json(".json/develop_get.json").json_load()
        if type_ is None:
            self.emb = discord.Embed(title="Топ 10 сервера")
            for row in self.db.get_from_user(ctx.guild.id, "Name", "Cash", "Lvl", "ID", order_by="Cash"):
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

            await ctx.reply(embed=self.emb)
        elif type_ == "chat":
            self.emb = discord.Embed(title="Топ 10 сервера по левелу")
            for row in self.db.get_from_user(ctx.guild.id, "Name", "ChatLevel", "ID", "Xp", order_by="Xp"):
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

            await ctx.reply(embed=self.emb)
        elif type_ == "voice":
            self.emb = discord.Embed(title="Топ 10 сервера по времени в голосовых каналах")
            for row in self.db.get_from_user(
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

            await ctx.reply(embed=self.emb)
        elif type_ == "rep":
            self.emb = discord.Embed(title="Топ 10 сервера")
            self.counter = 0
            for row in self.db.get_from_user(ctx.guild.id, "Name", "Reputation", order_by="Reputation", limit=10):
                self.counter += 1
                self.emb.add_field(
                    name=f'# {self.counter} | `{row[0]}`',
                    value=f'Репутация: {row[1]}',
                    inline=False
                )
            await ctx.reply(embed=self.emb)

    @commands.command(aliases=["cash"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __balance(
            self, ctx: commands.context.Context,
            member: discord.Member = None
    ) -> None:
        if member is None:
            try:
                await ctx.reply(
                    embed=create_emb(
                        title="Баланс",
                        description=f"Баланс пользователя ```{ctx.author}``` составляет "
                                    f"```{divide_the_number(self.db.get_cash(ctx.author.id, ctx.guild.id))}``` "
                                    f"DP коинов"
                    )
                )
            except TypeError:
                logging.error(f"TypeError: user.py 226 cash")
        else:
            await ctx.reply(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя ```{member}``` составляет "
                                f"```{divide_the_number(self.db.get_cash(member.id, ctx.guild.id))}``` DP коинов"
                )
            )

    @commands.command(aliases=["bank"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __bank(
            self, ctx: commands.context.Context,
            action: str = None, cash: Union[int, str] = None
    ) -> None:
        if action is None:
            self.all_cash = self.db.get_cash(ctx.author.id, ctx.guild.id) + self.db.get_cash(
                ctx.author.id, ctx.guild.id, bank=True
            )
            await ctx.reply(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя ```{ctx.author}``` составляет "
                                f"```{divide_the_number(self.db.get_cash(ctx.author.id, ctx.guild.id))}```"
                                f" DP коинов\n\nБаланс в банке составляет"
                                f"```{divide_the_number(self.db.get_cash(ctx.author.id, ctx.guild.id, bank=True))}``` "
                                f"DP коинов\n\nВсего коинов - `"
                                f"{divide_the_number(self.all_cash)}"
                )
            )
        elif action == "add":
            if await self.db.cash_check(ctx, cash):
                self.db.add_coins_to_the_bank(ctx.author.id, ctx.guild.id, cash)
                await ctx.message.add_reaction('✅')

        elif action == "take":
            if cash == "all":
                self.db.take_coins_from_the_bank(ctx.author.id, ctx.guild.id, "all")
            else:
                if cash is None:
                    await ctx.reply(f"""{ctx.author.mention}, Вы не ввели сумму!""")
                elif cash > self.db.get_cash(ctx.author.id, ctx.guild.id, bank=True):
                    await ctx.reply(f"""{ctx.author.mention}, у Вас недостаточно средств!""")
                if await self.db.cash_check(ctx, cash):
                    self.db.take_coins_from_the_bank(ctx.author.id, ctx.guild.id, cash)
                    await ctx.message.add_reaction('✅')

    @commands.command(aliases=['shop'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __shop(self, ctx: commands.context.Context):
        self.emb = discord.Embed(title="Магазин ролей")
        for row in self.db.get_from_shop(ctx.guild.id, "RoleID", "RoleCost", order_by="RoleCost"):
            if ctx.guild.get_role(row[0]) is not None:
                self.emb.add_field(
                    name=f'Роль {ctx.guild.get_role(row[0]).mention}',
                    value=f'Стоимость: **{row[1]} DP коинов**',
                    inline=False
                )
        self.emb.add_field(name="**Как купить роль?**",
                           value=f'''```diff\n- {PREFIX}buy <Упоминание роли>\n```''')
        self.db.get_from_item_shop(ctx.guild.id, "ItemID", "ItemName", "ItemCost", order_by="ItemCost")
        if self.db.get_from_item_shop(
                ctx.guild.id,
                "ItemID",
                "ItemName",
                "ItemCost",
                order_by="ItemCost"
        ).fetchone() is not None:
            self.emb.add_field(name='**Другое:**\n', value="Сообщение о покупке придет администрации!", inline=False)
            for row in self.db.get_from_item_shop(ctx.guild.id, "ItemID", "ItemName", "ItemCost", order_by="ItemCost"):
                self.emb.add_field(
                    name=f'**{row[1]}**',
                    value=f'Стоимость: **{row[2]} DP коинов**\n'
                          f'Чтобы купить {PREFIX}buy_item {row[0]}',
                    inline=False
                )

        self.emb.add_field(
            name="**Чтобы купить роль:**",
            value=f"```diff\n- {PREFIX}buy @роль, которую Вы хотите купить\n```")
        await ctx.reply(embed=self.emb)

    @commands.command(aliases=["buy_item"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy_item(self, ctx: commands.context.Context, item: int = None):
        if item is None:
            await ctx.reply(f"""{ctx.author}, укажите то, что Вы хотите приобрести""")
        else:
            self.db.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="ItemCost")
            if self.db.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="ItemCost").fetchone() is None:
                await ctx.reply(f"""{ctx.author}, такого товара не существует!""")
            elif self.db.get_item_from_item_shop(
                    ctx.guild.id, item, "*", order_by="ItemCost"
            ).fetchone()[0] > self.db.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.reply(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.db.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.db.get_item_from_item_shop(ctx.guild.id, item, "ItemCost", order_by="ItemCost")
                )
                await ctx.message.add_reaction('✅')
                channel = self.bot.get_channel(self.db.get_from_server(ctx.guild.id, "ChannelID"))
                await channel.send(f"Покупка {ctx.author.mention} товар номер {item}")
                await ctx.reply("Администрация скоро выдаст Вам товар")

    @commands.command(aliases=["buy", "buy-role"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy(self, ctx: commands.context.Context, role: discord.Role = None):
        if role is None:
            await ctx.reply(f"""{ctx.author}, укажите роль, которую Вы хотите приобрести""")
        else:
            if role in ctx.author.roles:
                await ctx.reply(f"""{ctx.author}, у Вас уже есть эта роль!""")
            elif self.db.get_from_shop(
                    ctx.author.id, str(ctx.guild.id), "RoleCost", order_by="RoleCost"
            ).fetchone() is None:
                pass
            elif self.db.get_from_shop(
                    ctx.author.id, str(ctx.guild.id), "RoleCost", order_by="RoleCost"
            ).fetchone()[0] > self.db.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.reply(f"""{ctx.author}, у Вас недостаточно средств для покупки этой роли!""")
            else:
                await ctx.author.add_roles(role)
                self.db.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.db.get_from_shop(
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
            self, ctx: commands.context.Context,
            member: discord.Member = None, cash: int = None
    ) -> None:
        if member is None:
            await ctx.reply(f"""{ctx.author}, укажите пользователя, которому Вы хотите перевести коины""")
        else:
            if await self.db.cash_check(ctx, cash, check=True):
                if member.id == ctx.author.id:
                    await ctx.reply(f"""{ctx.author}, Вы не можете перевести деньги себе""")
                else:
                    self.db.take_coins(ctx.author.id, ctx.guild.id, cash)
                    self.db.add_coins(member.id, ctx.guild.id, cash)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["stats"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __stats(self, ctx: commands.context.Context, member: discord.Member = None) -> None:
        self.ID = ctx.author.id if member is None else member.id
        self.guild_id = ctx.guild.id if member is None else member.guild.id
        self.lvl = self.db.get_stat(self.ID, self.guild_id, "ChatLevel")
        self.all_xp = self.db.get_user_xp(ctx.author.id if member is None else member.id, ctx.guild.id)
        self.xp = self.db.get_xp(self.lvl + 1) - self.all_xp
        await ctx.reply(
            embed=create_emb(
                title="Статистика {}".format(ctx.author if member is None else member),
                args=[
                    {
                        "name": f'Coinflips - {self.db.get_stat(self.ID, self.guild_id, "CoinFlipsCount")}',
                        "value": f'Wins - {self.db.get_stat(self.ID, self.guild_id, "CoinFlipsCount")}\n '
                                 f'Loses - {self.db.get_stat(self.ID, self.guild_id, "CoinFlipsLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'Rust casinos - {self.db.get_stat(self.ID, self.guild_id, "RustCasinosCount")}',
                        "value": f'Wins - {self.db.get_stat(self.ID, self.guild_id, "RustCasinoWinsCount")}\n '
                                 f'Loses - {self.db.get_stat(self.ID, self.guild_id, "RustCasinoLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'Rolls - {self.db.get_stat(self.ID, self.guild_id, "RollsCount")}',
                        "value": f'Wins - {self.db.get_stat(self.ID, self.guild_id, "RollsWinsCount")}\n '
                                 f'Loses - {self.db.get_stat(self.ID, self.guild_id, "RollsLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'Fails - {self.db.get_stat(self.ID, self.guild_id, "FailsCount")}',
                        "value": f'Wins - {self.db.get_stat(self.ID, self.guild_id, "FailsWinsCount")}\n '
                                 f'Loses - {self.db.get_stat(self.ID, self.guild_id, "FailsLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": f'777s - {self.db.get_stat(self.ID, self.guild_id, "ThreeSevensCount")}',
                        "value": f'Wins - {self.db.get_stat(self.ID, self.guild_id, "ThreeSevensWinsCount")}\n '
                                 f'Loses - {self.db.get_stat(self.ID, self.guild_id, "ThreeSevensLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": 'Побед/Поражений всего',
                        "value": f'Wins - {self.db.get_stat(self.ID, self.guild_id, "AllWinsCount")}\n '
                                 f'Loses - {self.db.get_stat(self.ID, self.guild_id, "AllLosesCount")}',
                        "inline": True
                    },
                    {
                        "name": 'Выиграно всего',
                        "value": divide_the_number(
                            self.db.get_stat(
                                self.ID,
                                self.guild_id,
                                "EntireAmountOfWinnings"
                            )
                        ),
                        "inline": True
                    },
                    {
                        "name": 'Минут в голосовых каналах',
                        "value": f'{self.db.get_stat(self.ID, self.guild_id, "MinutesInVoiceChannels")} минут',
                        "inline": True
                    },
                    {
                        "name": 'Сообщений в чате',
                        "value": f'{self.db.get_stat(self.ID, self.guild_id, "MessagesCount")} сообщений в чате',
                        "inline": True
                    },
                    {
                        "name": f'{self.lvl} левел в чате',
                        "value": f'{divide_the_number(self.xp)} опыта до следующего левела, '
                                 f'{divide_the_number(self.all_xp)} опыта всего',
                        "inline": True
                    }
                ]
            )
        )

    @commands.command(aliases=["card"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __card(self, ctx: commands.context.Context) -> None:
        self.img = Image.new("RGBA", (500, 300), "#323642")
        self.response = requests.get(str(ctx.author.avatar.url)[:-10], stream=True)
        self.response = Image.open(io.BytesIO(self.response.content))
        self.response = self.response.convert("RGBA")
        self.response = self.response.resize((100, 100), Image.ANTIALIAS)
        self.response.save(f".intermediate_files/avatar{ctx.author.id}.png")

        self.avatar = Image.open(f'.intermediate_files/avatar{ctx.author.id}.png')
        self.avatar = crop(self.avatar, (100, 100))
        self.avatar.putalpha(prepare_mask((100, 100), 4))
        self.avatar.save(f'.intermediate_files/out_avatar{ctx.author.id}.png')

        self.img.alpha_composite(
            self.response, (15, 15)
        )

        self.image_draw = ImageDraw.Draw(self.img)
        self.wins = 0
        self.loses = 0
        self.minutes_in_voice = 0
        self.messages = 0

        for i in self.db.get_card(ctx.author.id, ctx.guild.id):
            self.wins += i[0]
            self.loses += i[1]
            self.minutes_in_voice += i[2]
            self.messages += i[3]

        self.image_draw.text(
            (130, 15),
            f"{ctx.author.name}#{ctx.author.discriminator}",
            font=ImageFont.truetype('calibri.ttf', size=30)
        )
        self.image_draw.text(
            (130, 45),
            f"ID: {ctx.author.id}",
            font=ImageFont.truetype("calibri.ttf", size=20)
        )
        self.image_draw.text(
            (15, 125),
            f"Wins: {self.wins}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        self.image_draw.text(
            (15, 160),
            f"Loses: {divide_the_number(self.loses)}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        self.image_draw.text(
            (15, 195),
            f"Minutes in voice: {divide_the_number(self.minutes_in_voice)}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        self.image_draw.text(
            (15, 230),
            f"Messages: {divide_the_number(self.messages)}",
            font=ImageFont.truetype("calibrib.ttf", size=25)
        )
        self.images = []
        self.verification,  self.developer, self.coder = \
            self.db.get_from_card(ctx.author.id, "Verification", "Developer", "Coder")
        if int(self.verification) == 1:
            self.image = Image.open("files/green_galka.png")
            self.image = self.image.convert("RGBA")
            self.image = self.image.resize((30, 30), Image.ANTIALIAS)
            self.images.append(self.image)
        elif int(self.verification) == 2:
            self.image = Image.open("files/galka.png")
            self.image = self.image.convert("RGBA")
            self.image = self.image.resize((30, 30), Image.ANTIALIAS)
            self.images.append(self.image)
        if int(self.developer) == 1:
            self.image = Image.open("files/developer.png")
            self.image = self.image.convert("RGBA")
            self.image = self.image.resize((30, 30), Image.ANTIALIAS)
            self.images.append(self.image)
        if int(self.coder) == 1:
            self.image = Image.open("files/cmd.png")
            self.image = self.image.convert("RGBA")
            self.image = self.image.resize((30, 30), Image.ANTIALIAS)
            self.images.append(self.image)
        if len(self.images) != 0:
            self.x = 128
            for i in range(len(self.images)):
                self.img.alpha_composite(self.images[i], (self.x, 70))
                self.x += 35

        self.img.save(f'.intermediate_files/user_card{ctx.author.id}.png')

        await ctx.reply(file=discord.File(fp=f'.intermediate_files/user_card{ctx.author.id}.png'))
        os.remove(f".intermediate_files/user_card{ctx.author.id}.png")
        os.remove(f".intermediate_files/avatar{ctx.author.id}.png")
        os.remove(f".intermediate_files/out_avatar{ctx.author.id}.png")

    @commands.command(aliases=["promo"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_active(self, ctx: commands.context.Context, promo: str = None):
        if promo is None:
            await ctx.reply(f"""{ctx.author.mention}, Вы не ввели промокод!""")
        elif not self.db.checking_for_promo_code_existence_in_table(promo):
            await ctx.reply(f"""{ctx.author.mention}, такого промокода не существует!""")
        elif self.db.get_from_promo_codes(promo, "Global") == 0 and \
                ctx.guild.id != self.db.get_from_promo_codes(promo, "GuildID"):
            await ctx.reply(
                f"""{ctx.author.mention}, Вы не можете использовать этот промокод на этом данном сервере!"""
            )
        else:
            self.cash = self.db.get_from_promo_codes(promo, "Cash")
            self.db.add_coins(ctx.author.id, ctx.guild.id, self.cash)
            self.db.delete_from_promo_codes(promo)
            self.emb = discord.Embed(title="Промокод", colour=get_color(ctx.author.roles))
            self.emb.add_field(
                name=f'Промокод активирован!',
                value=f'Вам начислено **{divide_the_number(self.cash)}** коинов!',
                inline=False
            )
            await ctx.reply(embed=self.emb)

    @commands.command(aliases=['gift'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __gift(
            self, ctx: commands.context.Context,
            member: discord.Member = None, role: discord.Role = None
    ) -> None:
        if role is None:
            await ctx.reply(f"""{ctx.author}, укажите роль, которую Вы хотите приобрести""")
        elif member is None:
            await ctx.reply(f"""{ctx.author}, укажите человека, которому Вы хотите подарить роль""")
        else:
            if role in member.roles:
                await ctx.reply(f"""{ctx.author}, у Вас уже есть эта роль!""")

            elif self.db.get_from_shop(ctx.guild.id, "RoleCost", order_by="RoleCost", role_id=role.id).fetchone()[0] > \
                    self.db.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.reply(f"""{ctx.author}, у Вас недостаточно денег для покупки этой роли!""")
            else:
                await member.add_roles(role)
                self.db.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.db.get_from_shop(
                        ctx.guild.id, "RoleCost", order_by="RoleCost", role_id=role.id
                                       ).fetchone()[0]
                )
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["promos"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_codes(self, ctx: commands.context.Context) -> None:
        if ctx.guild is None:
            if not self.db.checking_for_promo_code_existence_in_table_by_id(ctx.author.id):
                await ctx.author.send(f"{ctx.author.mention}, у Вас нет промокодов!")
            else:
                self.emb = discord.Embed(title="Промокоды")
                for codes in self.db.get_from_promo_codes("", ["Code", "GuildID", "Cash"], ID=ctx.author.id):
                    for guild in self.bot.guilds:
                        if guild.id == codes[1]:
                            self.server = guild
                            break
                    if self.server is not None:
                        self.emb.add_field(
                            name=f"{self.server} - {divide_the_number(codes[2])}",
                            value=f"{codes[0]}",
                            inline=False
                        )
                await ctx.author.send(embed=self.emb)
        else:
            await ctx.reply(f"{ctx.author.mention}, эту команду можно использовать только в личных сообщениях бота")

    @commands.command(aliases=["promo_create"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_create(self, ctx: commands.context.Context, cash: int = None, key: str = None) -> None:
        if cash is None:
            await ctx.reply(f'{ctx.author.mention}, Вы не ввели сумму!')
        elif cash > self.db.get_cash(ctx.author.id, ctx.guild.id):
            await ctx.reply(f"""{ctx.author.mention}, у Вас недостаточно денег для создания промокода!""")
        elif cash < 1:
            await ctx.reply(f"""{ctx.author.mention}, не-не-не:)""")
        elif ctx.guild is None:
            pass
        else:
            self.code = get_promo_code(10)
            if key == "global" and ctx.author.id == 401555829620211723:
                self.db.insert_into_promo_codes(ctx.author.id, ctx.guild.id, str(self.code), cash, 1)
            else:
                self.db.insert_into_promo_codes(ctx.author.id, ctx.guild.id, str(self.code), cash, 0)
                self.db.take_coins(ctx.author.id, ctx.guild.id, cash)
            try:
                await ctx.author.send(self.code)
                self.emb = discord.Embed(title="Промокод", colour=get_color(ctx.author.roles))
                self.emb.add_field(
                    name=f'Ваш промокод на **{divide_the_number(cash)}**',
                    value=f'Промокод отправлен Вам в личные сообщения!',
                    inline=False
                )
                await ctx.reply(embed=self.emb)
            except discord.Forbidden:
                self.code2 = self.code
                self.code = ""
                for i in range(len(self.code2)):
                    if i > len(self.code2) - 4:
                        self.code += "*"
                    else:
                        self.code += self.code2[i]
                self.emb = discord.Embed(title="Промокод", colour=get_color(ctx.author.roles))
                self.emb.add_field(
                    name=f'Ваш промокод на **{divide_the_number(cash)}**',
                    value=f'{divide_the_number(self.code)}\nЧтобы получить все Ваши промокоды, '
                          f'Вы можете написать //promos в личные сообщения бота\nЕсли у Вас возникнет ошибка отправки, '
                          f'Вам необходимо включить личные сообщения от участников сервера, после отправки сообщения '
                          f'эту функцию можно выключить.',
                    inline=False
                )
                await ctx.reply(embed=self.emb)

    @commands.command(aliases=["gpt"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def __gpt(self, ctx: commands.context.Context, message: str) -> None:
        if ctx.guild is not None:
            if self.db.get_cash(ctx.author.id, ctx.guild.id) < 10000:
                await ctx.reply("NO MAMA")
                return
            if ctx.author.id not in self.gpt_users.keys():
                self.gpt_users[ctx.author.id] = GTP3Model(self.gpt_token)
            self.db.take_coins(ctx.author.id, ctx.guild.id, 10000)
            await ctx.reply(self.gpt_users[ctx.author.id].answer(message))
        else:
            await ctx.reply(f"{ctx.author.mention}, эту команду нельзя использовать в личных сообщениях бота")

    @commands.command(aliases=["gpt-context"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def __gpt(self, ctx: commands.context.Context, message: str) -> None:
        if ctx.guild is not None:
            if self.db.get_cash(ctx.author.id, ctx.guild.id) < 20000:
                await ctx.reply("NO MAMA")
                return
            if ctx.author.id not in self.gpt_users.keys():
                self.gpt_users[ctx.author.id] = GTP3Model(self.gpt_token)
            self.db.take_coins(ctx.author.id, ctx.guild.id, 20000)
            await ctx.reply(self.gpt_users[ctx.author.id].answer_with_context(message))
        else:
            await ctx.reply(f"{ctx.author.mention}, эту команду нельзя использовать в личных сообщениях бота")
