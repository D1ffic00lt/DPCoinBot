import os
import discord

from discord.ext import commands
from discord import app_commands

from botsections.functions.helperfunction import get_time, write_log, create_emb, divide_the_number, get_color
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
                                f"```{divide_the_number(self.db.get_cash(inter.user.id, inter.guild.id, bank=True))}``` "
                                f"DP коинов\n\nВсего коинов - `"
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
