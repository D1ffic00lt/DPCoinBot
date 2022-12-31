import discord

from discord.ext import commands
from discord.utils import get
from discord import app_commands

from botsections.functions.additions import get_time, write_log
from database.db import Database

__all__ = (
    "AdminSlash",
)


class AdminSlash(commands.Cog):
    NAME = 'admin slash module'

    __slots__ = (
        "db", "bot", "role",
        "msg", "ind"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.role: discord.Role
        self.db: Database = db
        self.bot = bot
        self.msg: str
        self.ind: int
        self.administrator_role_id: int
        print(f"[{get_time()}] [INFO]: AdminSlash connected")
        write_log(f"[{get_time()}] [INFO]: AdminSlash connected")

    @app_commands.command(name="give")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give(self, inter: discord.Interaction, member: discord.Member, cash: int) -> None:
        self.administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(self.administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                self.role = discord.utils.get(inter.guild.roles, id=self.administrator_role_id)
                if self.role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if await self.db.cash_check(inter, cash, max_cash=1000000):
            self.db.add_coins(member.id, inter.guild.id, cash)
            await inter.response.send_message('✅')

    @app_commands.command(name="take")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take(self, inter: discord.Interaction, member: discord.Member, cash: str) -> None:
        self.administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(self.administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                self.role = discord.utils.get(inter.guild.roles, id=self.administrator_role_id)
                if self.role not in inter.user.roles:
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

    @app_commands.command(name="give-role")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give_role(self, inter: discord.Interaction, role: discord.Role, cash: int) -> None:
        self.administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(self.administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                self.role = discord.utils.get(inter.guild.roles, id=self.administrator_role_id)
                if self.role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if await self.db.cash_check(inter, cash, max_cash=1000000):
            for member in inter.guild.members:
                if get(member.roles, id=role.id):
                    self.db.add_coins(member.id, inter.guild.id, cash)
            await inter.response.send_message('✅')

    @app_commands.command(name="take-role")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take_role(self, inter: discord.Interaction, role: discord.Role, cash: str) -> None:
        self.administrator_role_id = self.db.get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(self.administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            else:
                self.role = discord.utils.get(inter.guild.roles, id=self.administrator_role_id)
                if self.role not in inter.user.roles:
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

    @app_commands.command(name="remove-shop")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_shop(self, inter: discord.Interaction, role: discord.Role) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            self.db.delete_from_shop(role.id, inter.guild.id)
            await inter.response.send_message('✅')

    @app_commands.command(name="add-shop")
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

    @app_commands.command(name="add-else")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_item_shop(self, inter: discord.Interaction, item: str, price: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            self.msg = item
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
                    self.db.insert_into_item_shop(1, str(self.msg), inter.guild.id, price)
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
                    self.ind = max([
                        i[0] for i in self.db.get_from_item_shop(
                            inter.guild.id, "ItemID", order_by="ItemID").fetchall()
                    ])
                    self.db.insert_into_item_shop(self.ind + 1, str(self.msg), inter.guild.id, price)
                    await inter.response.send_message('✅')

    @app_commands.command(name="remove-else")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_item_shop(self, inter: discord.Interaction, item_id: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            self.db.delete_from_item_shop(item_id, inter.guild.id)
            await inter.response.send_message('✅')
