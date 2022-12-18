import io
import os
import discord
import requests

from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageFont, ImageDraw

from botsections.functions.config import settings
from botsections.functions.helperfunction import get_time, write_log, create_emb, divide_the_number, get_color, crop, \
    prepare_mask, get_promo_code
from botsections.functions.json_ import Json
from database.db import Database

__all__ = (
    "UserSlash",
)


class UserSlash(commands.Cog):
    NAME = 'user slash module'

    __slots__ = (
        "db", "bot",
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.bot: commands.Bot = bot
        print(f"[{get_time()}] [INFO]: User (slash) connected")
        write_log(f"[{get_time()}] [INFO]: User (slash) connected")

    @app_commands.command(name="update", description="Информация об обновлении")
    @app_commands.guilds(493970394374471680)
    async def __update(self, inter: discord.Interaction):
        await inter.response.send_message("123")

    @app_commands.command(name="cash", description="сколько у тебя денех?")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __balance(
            self, inter: discord.Interaction,
            member: discord.Member = None
    ) -> None:
        if member is None:
            try:
                await inter.response.send_message(
                    embed=create_emb(
                        title="Баланс",
                        description=f"Баланс пользователя ```{inter.user}``` составляет "
                                    f"```{divide_the_number(self.db.get_cash(inter.user.id, inter.guild.id))}``` "
                                    f"DP коинов"
                    )
                )
            except TypeError:
                print(f"[{get_time()}] [ERROR]: TypeError: user.py 224 cash")
        else:
            await inter.response.send_message(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя ```{member}``` составляет "
                                f"```{divide_the_number(self.db.get_cash(member.id, inter.guild.id))}``` DP коинов"
                )
            )

    @app_commands.command(name="bank", description="сколько у тебя денех в банке?")
    @app_commands.guilds(493970394374471680)
    @app_commands.choices(action=[
        app_commands.Choice(name="Положить", value="add"),
        app_commands.Choice(name="Снять", value="take")
    ])
    async def __bank(
            self, inter: discord.Interaction,
            action: app_commands.Choice[str] = None,
            cash: int = None
    ) -> None:
        print(action, cash)
        if action is None:
            await inter.response.send_message(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя ```{inter.user}``` составляет "
                                f"```{divide_the_number(self.db.get_cash(inter.user.id, inter.guild.id))}```"
                                f" DP коинов\n\nБаланс в банке составляет"
                                f"```{divide_the_number(self.db.get_cash(inter.user.id, inter.guild.id, bank=True))}```"
                                f" DP коинов\n\nВсего коинов - `"
                                f"""{divide_the_number(
                                    self.db.get_cash(
                                        inter.user.id,
                                        inter.guild.id
                                    )
                                ) + divide_the_number(
                                    self.db.get_cash(
                                        inter.user.id,
                                        inter.guild.id,
                                        bank=True
                                    )
                                )}`"""
                )
            )
        elif action.value == "add":
            if await self.db.cash_check(inter, cash):
                self.db.add_coins_to_the_bank(inter.user.id, inter.guild.id, cash)
                await inter.response.send_message("✅")
        elif action.value == "take":
            if cash == "all":
                self.db.take_coins_from_the_bank(inter.user.id, inter.guild.id, "all")
            else:
                if cash is None:
                    await inter.response.send_message(f"""{inter.user.mention}, Вы не ввели сумму!""", ephemeral=True)
                elif int(cash) > self.db.get_cash(inter.user.id, inter.guild.id, bank=True):
                    await inter.response.send_message(
                        f"""{inter.user.mention}, у Вас недостаточно средств!""",
                        ephemeral=True
                    )
                if await self.db.cash_check(inter, cash):
                    self.db.take_coins_from_the_bank(inter.user.id, inter.guild.id, cash)
                    await inter.response.send_message("✅")

    @app_commands.command(name="slb")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __slb(self, inter: discord.Interaction) -> None:
        self.all_cash = 0
        self.color = get_color(inter.user.roles)
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json(".json/develop_get.json").json_load()
        for row in self.db.get_from_user(inter.guild.id, "Name", "Cash", "ID", order_by="Cash"):
            for member in inter.guild.members:
                if str(member) == row[0]:
                    self.name = member
                    break
            if self.name is not None and not self.name.bot:
                for member in inter.guild.members:
                    if self.name.id == member.id:
                        if self.name.id == 401555829620211723 and \
                                inter.guild.id == 493970394374471680 and self.js["slb"] is False:
                            pass
                        else:
                            self.all_cash += row[1]
                        break
        await inter.response.send_message(
            embed=create_emb(
                title="Общий баланс сервера:",
                color=self.color,
                args=[
                    {
                        "name": f"Баланс сервера {inter.guild}",
                        "value": f"Общий баланс сервера {inter.guild} составляет "
                                 f"{divide_the_number(self.all_cash)} "
                                 f" DP коинов",
                        "inline": False
                    }
                ]
            )
        )

    @app_commands.command(name="lb")
    @app_commands.guilds(493970394374471680)
    @app_commands.choices(mode=[
        app_commands.Choice(name="чат", value="chat"),
        app_commands.Choice(name="войс", value="voice"),
        app_commands.Choice(name="репутация", value="rep")
    ])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __lb(self, inter: discord.Interaction, mode: app_commands.Choice[str] = None) -> None:
        self.counter = 0
        self.name: discord.Member
        self.index = 0
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json(".json/develop_get.json").json_load()
        if mode is None:
            self.emb = discord.Embed(title="Топ 10 сервера")
            for row in self.db.get_from_user(inter.guild.id, "Name", "Cash", "Lvl", "ID", order_by="Cash"):
                if self.index == 10:
                    break
                for member in inter.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in inter.guild.members:
                        if member.id == row[3]:
                            if self.name.id == 401555829620211723 and inter.guild.id == 493970394374471680 \
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

            await inter.response.send_message(embed=self.emb)
        elif mode.value == "chat":
            self.emb = discord.Embed(title="Топ 10 сервера по левелу")
            for row in self.db.get_from_user(inter.guild.id, "Name", "ChatLevel", "ID", "Xp", order_by="Xp"):
                if self.index == 10:
                    break
                for member in inter.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in inter.guild.members:
                        if member.id == row[2]:
                            self.counter += 1
                            self.emb.add_field(
                                name=f'# {self.counter} | `{row[0]}` | chat lvl `{row[1]}`',
                                value=f'xp: **{divide_the_number(row[3])}**',
                                inline=False
                            )
                            self.index += 1
                            break

            await inter.response.send_message(embed=self.emb)
        elif mode.value == "voice":
            self.emb = discord.Embed(title="Топ 10 сервера по времени в голосовых каналах")
            for row in self.db.get_from_user(
                    inter.guild.id,
                    "Name",
                    "MinutesInVoiceChannels",
                    "ID",
                    order_by="MinutesInVoiceChannels"
            ):
                if self.index == 10:
                    break
                for member in inter.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in inter.guild.members:
                        if member.id == row[2]:
                            self.counter += 1
                            self.emb.add_field(
                                name=f'# {self.counter} | `{row[0]}`',
                                value=f'**{divide_the_number(row[1])} минут ({divide_the_number(row[1] / 60)} часов)**',
                                inline=False
                            )
                            self.index += 1
                            break

            await inter.response.send_message(embed=self.emb)
        elif mode.value == "rep":
            self.emb = discord.Embed(title="Топ 10 сервера")
            self.counter = 0
            for row in self.db.get_from_user(inter.guild.id, "Name", "Reputation", order_by="Reputation", limit=10):
                self.counter += 1
                self.emb.add_field(
                    name=f'# {self.counter} | `{row[0]}`',
                    value=f'Репутация: {row[1]}',
                    inline=False
                )
            await inter.response.send_message(embed=self.emb)

    @app_commands.command(name="shop")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __shop(self, inter: discord.Interaction):
        self.emb = discord.Embed(title="Магазин ролей")
        for row in self.db.get_from_shop(inter.guild.id, "RoleID", "RoleCost", order_by="RoleCost"):
            if inter.guild.get_role(row[0]) is not None:
                self.emb.add_field(
                    name=f'Роль {inter.guild.get_role(row[0]).mention}',
                    value=f'Стоимость: **{row[1]} DP коинов**',
                    inline=False
                )
        self.emb.add_field(
            name="**Как купить роль?**",
            value=f'''```diff\n- {settings["prefix"]}buy <Упоминание роли>\n```'''
        )
        self.db.get_from_item_shop(inter.guild.id, "ItemID", "ItemName", "ItemCost", order_by="ItemCost")
        if self.db.get_from_item_shop(
                inter.guild.id,
                "ItemID",
                "ItemName",
                "ItemCost",
                order_by="ItemCost"
        ).fetchone() is not None:
            self.emb.add_field(name='**Другое:**\n', value="Сообщение о покупке придет администрации!", inline=False)
            for row in self.db.get_from_item_shop(
                    inter.guild.id, "ItemID", "ItemName", "ItemCost", order_by="ItemCost"
            ):
                self.emb.add_field(
                    name=f'**{row[1]}**',
                    value=f'Стоимость: **{row[2]} DP коинов**\n'
                          f'Чтобы купить {settings["prefix"]}buy_item {row[0]}',
                    inline=False
                )

        self.emb.add_field(
            name="**Чтобы купить роль:**",
            value=f"```diff\n- {settings['prefix']}buy @роль, которую Вы хотите купить\n```")
        await inter.response.send_message(embed=self.emb)

    @app_commands.command(name="buy_item")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy_item(self, inter: discord.Interaction, item: int):
        self.db.get_item_from_item_shop(inter.guild.id, item, "*", order_by="ItemCost")
        if self.db.get_item_from_item_shop(inter.guild.id, item, "*", order_by="ItemCost").fetchone() is None:
            await inter.response.send_message(f"""{inter.user}, такого товара не существует!""", ephemeral=True)
        elif self.db.get_item_from_item_shop(
                inter.guild.id, item, "*", order_by="ItemCost"
        ).fetchone()[0] > self.db.get_cash(inter.user.id, inter.guild.id):
            await inter.response.send_message(f"""{inter.user}, у Вас недостаточно средств!""", ephemeral=True)
        else:
            self.db.take_coins(
                inter.user.id,
                inter.guild.id,
                self.db.get_item_from_item_shop(inter.guild.id, item, "ItemCost", order_by="ItemCost")
            )
            channel = self.bot.get_channel(self.db.get_from_server(inter.guild.id, "ChannelID"))
            await channel.send(f"Покупка {inter.user.mention} товар номер {item}")
            await inter.response.send_message("✅ Администрация скоро выдаст Вам товар! ✅")

    @app_commands.command(name="buy")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy(self, inter: discord.Interaction, role: discord.Role):
        if role is None:
            await inter.response.send_message(
                f"{inter.user}, укажите роль, которую Вы хотите приобрести", ephemeral=True
            )
        else:
            if role in inter.user.roles:
                await inter.response.send(f"{inter.user}, у Вас уже есть эта роль!", ephemeral=True)
            elif self.db.get_from_shop(
                    inter.user.id, str(inter.guild.id), "RoleCost", order_by="RoleCost"
            ).fetchone() is None:
                pass
            elif self.db.get_from_shop(
                    inter.user.id, str(inter.guild.id), "RoleCost", order_by="RoleCost"
            ).fetchone()[0] > self.db.get_cash(inter.user.id, inter.guild.id):
                await inter.response.send_message(
                    f"{inter.user}, у Вас недостаточно средств для покупки этой роли!",
                    ephemeral=True
                )
            else:
                await inter.user.add_roles(role)
                self.db.take_coins(
                    inter.user.id,
                    inter.guild.id,
                    self.db.get_from_shop(
                        inter.guild.id,
                        "RoleCost",
                        order_by="RoleCost",
                        role_id=role.id
                    )
                )
                await inter.response.send_message('✅')

    @app_commands.command(name="send")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send(
            self, inter: discord.Interaction,
            member: discord.Member, cash: int
    ) -> None:
        if await self.db.cash_check(inter, cash, check=True):
            if member.id == inter.user.id:
                await inter.response.send_message(
                    f"""{inter.user}, Вы не можете перевести деньги себе""", ephemeral=True
                )
            else:
                self.db.take_coins(inter.user.id, inter.guild.id, cash)
                self.db.add_coins(member.id, inter.guild.id, cash)
            await inter.response.send_message('✅')

    @app_commands.command(name="add_rep")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __good_rep(
            self, inter: discord.Interaction, member: discord.Member
    ) -> None:
        if member.id == inter.user.id:
            await inter.response.send_message(
                f"{inter.user}, Вы не можете повысить репутацию самому себе", ephemeral=True
            )
        else:
            self.db.add_reputation(inter.user.id, inter.guild.id, 1)
            await inter.response.send_message('✅')

    @app_commands.command(name="remove_rep")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __bad_rep(
            self, inter: discord.Interaction, member: discord.Member
    ) -> None:
        if member.id == inter.user.id:
            await inter.response.send_message(
                f"{inter.user}, Вы не можете понизить репутацию самому себе", ephemeral=True
                 )
        else:
            self.db.add_reputation(inter.user.id, inter.guild.id, -1)
            await inter.response.send_message('✅')

    @app_commands.command(name="stats")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __stats(self, inter: discord.Interaction, member: discord.Member = None) -> None:
        self.ID = inter.user.id if member is None else member.id
        self.guild_id = inter.guild.id if member is None else member.guild.id
        await inter.response.send_message(
            embed=create_emb(
                title="Статистика {}".format(inter.user if member is None else member),
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
                        "name": f'{self.db.get_stat(self.ID, self.guild_id, "ChatLevel")} левел в чате',
                        "value": '{} опыта до следующего левела, {} опыта всего',
                        "inline": True
                    }
                ]
            )
        )

    @app_commands.command(name="card")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __card(self, inter: discord.Interaction) -> None:
        self.img = Image.new("RGBA", (500, 300), "#323642")
        self.response = requests.get(str(inter.user.guild_avatar.url)[:-10], stream=True)
        self.response = Image.open(io.BytesIO(self.response.content))
        self.response = self.response.convert("RGBA")
        self.response = self.response.resize((100, 100), Image.ANTIALIAS)
        self.response.save(f".intermediate_files/avatar{inter.user.id}.png")

        self.avatar = Image.open(f'.intermediate_files/avatar{inter.user.id}.png')
        self.avatar = crop(self.avatar, (100, 100))
        self.avatar.putalpha(prepare_mask((100, 100), 4))
        self.avatar.save(f'.intermediate_files/out_avatar{inter.user.id}.png')

        self.img.alpha_composite(
            self.response, (15, 15)
        )

        self.image_draw = ImageDraw.Draw(self.img)
        self.wins = 0
        self.loses = 0
        self.minutes_in_voice = 0
        self.messages = 0

        for i in self.db.get_card(inter.user.id, inter.guild.id):
            self.wins += i[0]
            self.loses += i[1]
            self.minutes_in_voice += i[2]
            self.messages += i[3]

        self.image_draw.text(
            (130, 15),
            f"{inter.user.name}#{inter.user.discriminator}",
            font=ImageFont.truetype('calibri.ttf', size=30)
        )
        self.image_draw.text(
            (130, 45),
            f"ID: {inter.user.id}",
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
            self.db.get_from_card(inter.user.id, "Verification", "Developer", "Coder")
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

        self.img.save(f'.intermediate_files/user_card{inter.user.id}.png')

        await inter.response.send_message(
            file=discord.File(fp=f'.intermediate_files/user_card{inter.user.id}.png')
        )
        os.remove(f".intermediate_files/user_card{inter.user.id}.png")
        os.remove(f".intermediate_files/avatar{inter.user.id}.png")
        os.remove(f".intermediate_files/out_avatar{inter.user.id}.png")

    @app_commands.command(name="promo")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_active(self, inter: discord.Interaction, promo: str):
        if not self.db.checking_for_promo_code_existence_in_table(promo):
            await inter.response.send_message(
                f"""{inter.user.mention}, такого промокода не существует!""", ephemeral=True
            )
        elif self.db.get_from_promo_codes(promo, "Global") == 0 and \
                inter.guild.id != self.db.get_from_promo_codes(promo, "GuildID"):
            await inter.response.send_message(
                f"""{inter.user.mention}, Вы не можете использовать этот промокод на этом данном сервере!""",
                ephemeral=True
            )
        else:
            self.cash = self.db.get_from_promo_codes(promo, "Cash")
            self.db.add_coins(inter.user.id, inter.guild.id, self.cash)
            self.db.delete_from_promo_codes(promo)
            self.emb = discord.Embed(title="Промокод", colour=get_color(inter.user.roles))
            self.emb.add_field(
                name=f'Промокод активирован!',
                value=f'Вам начислено **{divide_the_number(self.cash)}** коинов!',
                inline=False
            )
            await inter.response.send_message(embed=self.emb)

    @app_commands.command(name="gift")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __gift(
            self, inter: discord.Interaction,
            member: discord.Member, role: discord.Role
    ) -> None:
        if role in member.roles:
            await inter.response.send_message(
                f"""{inter.user}, у Вас уже есть эта роль!""", ephemeral=True
            )
        elif self.db.get_from_shop(inter.guild.id, "RoleCost", order_by="RoleCost", role_id=role.id).fetchone()[0] > \
                self.db.get_cash(inter.user.id, inter.guild.id):
            await inter.response.send_message(
                f"""{inter.user}, у Вас недостаточно денег для покупки этой роли!""", ephemeral=True
            )
        else:
            await member.add_roles(role)
            self.db.take_coins(
                inter.user.id,
                inter.guild.id,
                self.db.get_from_shop(
                    inter.guild.id, "RoleCost", order_by="RoleCost", role_id=role.id
                ).fetchone()[0]
            )
            await inter.response.send_message('✅')

    @app_commands.command(name="promos")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_codes(self, inter: discord.Interaction) -> None:
        if not self.db.checking_for_promo_code_existence_in_table_by_id(inter.user.id):
            await inter.user.send(f"{inter.user.mention}, у Вас нет промокодов!")
        else:
            self.emb = discord.Embed(title="Промокоды")
            for codes in self.db.get_from_promo_codes("", ["Code", "GuildID", "Cash"], ID=inter.user.id):
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
            await inter.user.send(embed=self.emb)
            await inter.response.send_message('✅')

    @app_commands.command(name="promo_create")
    @app_commands.guilds(493970394374471680)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_create(self, inter: discord.Interaction, cash: int, key: str = None) -> None:
        if cash is None:
            await inter.response.send_message(
                f'{inter.user.mention}, Вы не ввели сумму!', ephemeral=True
            )
        elif cash > self.db.get_cash(inter.user.id, inter.guild.id):
            await inter.response.send_message(
                f"""{inter.user.mention}, у Вас недостаточно денег для создания промокода!""", ephemeral=True
            )
        elif cash < 1:
            await inter.response.send_message(
                f"""{inter.user.mention}, не-не-не:)""", ephemeral=True
            )
        elif inter.guild is None:
            pass
        else:
            self.code = get_promo_code(10)
            if key == "global" and inter.user.id == 401555829620211723:
                self.db.insert_into_promo_codes(inter.user.id, inter.guild.id, str(self.code), cash, 1)
            else:
                self.db.insert_into_promo_codes(inter.user.id, inter.guild.id, str(self.code), cash, 0)
                self.db.take_coins(inter.user.id, inter.guild.id, cash)
            try:
                await inter.user.send(self.code)
                self.emb = discord.Embed(title="Промокод", colour=get_color(inter.user.roles))
                self.emb.add_field(
                    name=f'Ваш промокод на **{divide_the_number(cash)}**',
                    value=f'Промокод отправлен Вам в личные сообщения!',
                    inline=False
                )
                await inter.response.send_message(embed=self.emb)
            except discord.Forbidden:
                self.code2 = self.code
                self.code = ""
                for i in range(len(self.code2)):
                    if i > len(self.code2) - 4:
                        self.code += "*"
                    else:
                        self.code += self.code2[i]
                self.emb = discord.Embed(title="Промокод", colour=get_color(inter.user.roles))
                self.emb.add_field(
                    name=f'Ваш промокод на **{divide_the_number(cash)}**',
                    value=f'{divide_the_number(self.code)}\nЧтобы получить все Ваши промокоды, '
                          f'Вы можете написать //promos в личные сообщения бота\nЕсли у Вас возникнет ошибка отправки, '
                          f'Вам необходимо включить личные сообщения от участников сервера, после отправки сообщения '
                          f'эту функцию можно выключить.',
                    inline=False
                )
                await inter.response.send_message(embed=self.emb)
