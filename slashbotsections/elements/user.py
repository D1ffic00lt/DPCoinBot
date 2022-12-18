from typing import Union, Any

import discord
from discord.ext import commands
from discord import app_commands

from botsections.functions.helperfunction import get_time, write_log, create_emb, divide_the_number
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
                await inter.response.send_message("yes")
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
                    await inter.response.send_message("yes")
