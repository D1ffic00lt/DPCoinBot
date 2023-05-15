# -*- coding: utf-8 -*-
import logging
import discord

from discord.ext import commands
from discord.utils import get
from discord import app_commands


__all__ = (
    "AdminSlash",
)


class AdminSlash(commands.Cog):
    NAME = 'admin slash module'

    __slots__ = (
        "db", "bot"
    )

    def __init__(self, bot: commands.Bot, db, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.bot = bot
        logging.info(f"Admin (Slash) connected")

    @app_commands.command(name="give", description="Выдать коины")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give(self, inter: discord.Interaction, member: discord.Member, cash: int) -> None:
        administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if await self.db.cash_check(inter, cash, max_cash=1000000):
            self.db.add_coins(member.id, inter.guild.id, cash)
            await inter.response.send_message('✅')

    @app_commands.command(name="take", description="Снять коины")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take(self, inter: discord.Interaction, member: discord.Member, cash: str) -> None:
        administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if await self.db.cash_check(inter, cash, max_cash=1000000):
            if cash != "all" and not cash.isdigit():
                return
            elif cash == "all":
                self.db.take_coins(member.id, inter.guild.id, self.db.get_cash(member.id, inter.guild.id))
            else:
                self.db.take_coins(member.id, inter.guild.id, int(cash))
            await inter.response.send_message('✅')

    @app_commands.command(name="give-role", description="Выдать коины по роли")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give_role(self, inter: discord.Interaction, role: discord.Role, cash: int) -> None:
        administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if await self.db.cash_check(inter, cash, max_cash=1000000):
            for member in inter.guild.members:
                if get(member.roles, id=role.id):
                    self.db.add_coins(member.id, inter.guild.id, cash)
            await inter.response.send_message('✅')

    @app_commands.command(name="take-role", description="Забрать коины по роли")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take_role(self, inter: discord.Interaction, role: discord.Role, cash: str) -> None:
        administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if await self.db.cash_check(inter, cash, max_cash=1000000):
            if cash == "all":
                for member in inter.guild.members:
                    if get(member.roles, id=role.id):
                        self.db.take_coins(
                            member.id,
                            inter.guild.id,
                            self.db.get_cash(member.id, inter.guild.id)
                        )
                await inter.response.send_message('✅')
            elif not cash.isdigit():
                return
            else:
                for member in inter.guild.members:
                    if get(member.roles, id=role.id):
                        self.db.take_coins(member.id, inter.guild.id, int(cash))
                await inter.response.send_message('✅')

    @app_commands.command(name="remove-shop", description="Удалить роль из магазина")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_shop(self, inter: discord.Interaction, role: discord.Role) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            self.db.delete_from_shop(role.id, inter.guild.id)
            await inter.response.send_message('✅')

    @app_commands.command(name="add-shop", description="Добавить роль в магазин")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_shop(self, inter: discord.Interaction, role: discord.Role, price: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            if price < 1:
                await inter.response.send_message(
                    f"""{inter.user}, ах ты проказник! Введите цену дольше 1""",
                    ephemeral=True
                )
            elif price > 100000:
                await inter.response.send_message(
                    f'{inter.user}, нельзя начислить больше 1.000.000 DP коинов!',
                    ephemeral=True
                )
            else:
                self.db.insert_into_shop(role.id, inter.guild.id, price)
                await inter.response.send_message('✅')

    @app_commands.command(name="add-else", description="Добавить предмет в магазин")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_item_shop(self, inter: discord.Interaction, item: str, price: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            msg = item
            if self.db.get_from_item_shop(inter.guild.id, "ItemID", order_by="ItemID").fetchone() is None:
                if price < 1:
                    await inter.response.send_message(
                        f"""{inter.user}, ах ты проказник! Введите цену дольше 1""", ephemeral=True
                    )
                elif price > 1000000:
                    await inter.response.send_message(
                        f'{inter.user}, нельзя начислить больше 1.000.000 DP коинов!', ephemeral=True
                    )
                else:
                    self.db.insert_into_item_shop(1, str(msg), inter.guild.id, price)
                    await inter.response.send_message('✅')
            else:
                if price < 1:
                    await inter.response.send_message(
                        f"""{inter.user}, ах ты проказник! Введите цену дольше 1""", ephemeral=True
                    )
                elif price > 1000000:
                    await inter.response.send_message(
                        f'{inter.user}, нельзя начислить больше 1.000.000 DP коинов!', ephemeral=True
                    )
                else:
                    ind = max([
                        i[0] for i in self.db.get_from_item_shop(
                            inter.guild.id, "ItemID", order_by="ItemID").fetchall()
                    ])
                    self.db.insert_into_item_shop(ind + 1, str(msg), inter.guild.id, price)
                    await inter.response.send_message('✅')

    @app_commands.command(name="remove-else", description="Удалить вещь из магазина")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_item_shop(self, inter: discord.Interaction, item_id: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            self.db.delete_from_item_shop(item_id, inter.guild.id)
            await inter.response.send_message('✅')
