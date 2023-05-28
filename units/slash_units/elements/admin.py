# -*- coding: utf-8 -*-
import logging
import discord

from discord.ext import commands
from discord.utils import get
from discord import app_commands
from typing import Union
from sqlalchemy import select, delete

from database.guild.item_shops import ShopItem
from database.guild.servers import ServerSettings
from database.guild.shops import ShopRole
from database.user.users import User
from units.additions import divide_the_number


__all__ = (
    "AdminSlash",
)


class AdminSlash(commands.Cog):
    NAME = 'admin slash module'

    __slots__ = (
        "db", "bot"
    )

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session = session
        self.bot = bot
        logging.info(f"Admin (Slash) connected")

    async def _get_administrator_role_id(self, guild_id: int) -> ServerSettings | bool:
        async with self.session() as session:
            async with session.begin():
                guild = await session.execute(
                    select(ServerSettings).where(
                        ServerSettings.guild_id == guild_id
                    )
                )
                guild = guild.scalars().first()
                if not guild:
                    return False
                return guild

    async def _check_cash(
            self, inter: discord.Interaction,
            cash: Union[str, int], max_cash: int = None,
            min_cash: int = 1, check: bool = False
    ) -> bool:
        mention = inter.user.mention
        author_id = inter.user.id
        if cash is None:
            message = f"{mention}, Вы не ввели сумму!"
            await inter.response.send_message(message, ephemeral=True)
            return
        async with self.session() as session:
            user = await session.execute(
                select(User).where(User.user_id == inter.user.id and User.guild_id == inter.guild.id)
            )
            user: User = user.scalars().first()
            if not user:
                await inter.response.send_message("no user", ephemeral=True)
                return False
        if check and cash > user.cash:
            message = f"{mention}, у Вас недостаточно средств!"
            await inter.response.send_message(message, ephemeral=True)
        else:
            if cash == "all":
                return True
            elif max_cash is not None:
                if (int(cash) < min_cash or int(cash) > max_cash) and author_id != 401555829620211723:
                    message = f'{mention}, нельзя ввести число меньше ' \
                              f'{divide_the_number(min_cash)} и больше {divide_the_number(max_cash)}!'
                    await inter.response.send_message(message, ephemeral=True)
                else:
                    return True
            elif max_cash is None:
                if int(cash) < min_cash and inter.user.id != 401555829620211723:
                    message = f'{mention}, нельзя ввести число меньше {divide_the_number(min_cash)}!'
                    await inter.response.send_message(message, ephemeral=True)
                else:
                    return True
        return False

    @app_commands.command(name="give", description="Выдать коины")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give(self, inter: discord.Interaction, member: discord.Member, cash: int) -> None:
        administrator_role_id = self._get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if member is None:
            await inter.response.send_message(f'{inter.user.mention}, укажите пользователя!')
            return
        if cash is None:
            await inter.response.send_message(f'{inter.user.mention}, укажите сумму!')
            return

        if await self._check_cash(inter, cash, max_cash=1000000):
            async with self.session() as session:
                async with session.begin():
                    user: User = await session.execute(
                        select(User).where(
                            User.guild_id == inter.guild.id and User.user_id == member.id
                        )
                    )
                    if not user:
                        return

                    user.cash += cash
            await inter.response.send_message('✅')

    @app_commands.command(name="take", description="Снять коины")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take(self, inter: discord.Interaction, member: discord.Member, cash: str) -> None:
        administrator_role_id = self._get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if member is None:
            await inter.response.send_message(f'{inter.user}, укажите пользователя!')
            return
        if cash is None:
            await inter.response.send_message(f'{inter.user}, укажите сумму!')
            return
        if await self._check_cash(inter, cash, max_cash=1000000):
            async with self.session() as session:
                async with session.begin():
                    user = await session.execute(
                        select(User).where(
                            User.guild_id == inter.guild.id and User.user_id == member.id
                        )
                    )
                    user: User = user.scalars().first()
                    if not user:
                        return
                    if cash == "all":
                        user.cash = 0
                    else:
                        user.cash -= cash
            await inter.response.send_message('✅')

    @app_commands.command(name="give-role", description="Выдать коины по роли")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give_role(self, inter: discord.Interaction, role: discord.Role, cash: int) -> None:
        administrator_role_id = self._get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            if role is None:
                await inter.response.send_message(f'{inter.user}, укажите роль!')
                return
            if cash is None:
                await inter.response.send_message(f'{inter.user}, укажите сумму!')
                return
            if await self._check_cash(inter, cash, max_cash=1000000):
                for member in inter.guild.members:
                    if get(member.roles, id=role.id):
                        async with self.session() as session:
                            async with session.begin():
                                user = await session.execute(
                                    select(User).where(
                                        User.guild_id == inter.guild.id and User.user_id == member.id
                                    )
                                )
                                user: User = user.scalars().first()
                                if not user:
                                    return
                                if cash == "all":
                                    user.cash = 0
                                else:
                                    user.cash -= cash
                await inter.response.send_message('✅')

    @app_commands.command(name="take-role", description="Забрать коины по роли")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take_role(self, inter: discord.Interaction, role: discord.Role, cash: str) -> None:
        administrator_role_id = self._get_administrator_role_id(inter.guild.id)  # !
        if inter.user.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not inter.user.guild_permissions.administrator:
                    await inter.response.send_message("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(inter.guild.roles, id=administrator_role_id)
                if role not in inter.user.roles:
                    await inter.response.send_message("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if role is None:
            await inter.response.send_message(f'{inter.user}, укажите роль!')
            return
        if cash is None:
            await inter.response.send_message(f"{inter.user.mention}, укажите сумму!")
            return
        if await self._check_cash(inter, cash, max_cash=1000000):
            async with self.session() as session:
                async with session.begin():
                    for member in inter.guild.members:
                        if get(member.roles, id=role.id):
                            user = await session.execute(
                                select(User).where(
                                    User.guild_id == inter.guild.id and User.user_id == member.id
                                )
                            )
                            user: User = user.scalars().first()
                            if not user:
                                continue
                            if cash == "all":
                                user.cash = 0
                            else:
                                user.cash -= cash
            await inter.response.send_message('✅')

    @app_commands.command(name="remove-shop", description="Удалить роль из магазина")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_shop(self, inter: discord.Interaction, role: discord.Role) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            if role is None:
                await inter.response.send_message(
                    f"""{inter.user}, укажите роль, которую Вы хотите удалить из магазина"""
                )
            else:
                async with self.session() as session:
                    async with session.begin():
                        await session.execute(
                            delete(ShopRole).where(ShopRole.role_id == role.id)
                        )
                await inter.response.send_message('✅')

    @app_commands.command(name="add-shop", description="Добавить роль в магазин")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_shop(self, inter: discord.Interaction, role: discord.Role, price: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            if role is None:
                await inter.response.send_message(
                    f"""{inter.user}, укажите роль, которую Вы хотите добавить в магазин"""
                )
            else:
                if price is None:
                    await inter.response.send_message(f"""{inter.user}, введите цену роли""")
                elif price < 1:
                    await inter.response.send_message(f"""{inter.user}, ах ты проказник! Введите цену дольше 1""")
                elif price > 100000:
                    await inter.response.send_message(f'{inter.user}, нельзя начислить больше 1.000.000 DP коинов!')
                else:
                    async with self.session() as session:
                        async with session.begin():
                            new_role_in_shop = ShopRole()
                            new_role_in_shop.role_id = role.id
                            new_role_in_shop.guild_id = inter.guild.id
                            new_role_in_shop.role_price = price
                            session.add(new_role_in_shop)
                    await inter.response.send_message('✅')

    @app_commands.command(name="add-else", description="Добавить предмет в магазин")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_item_shop(self, inter: discord.Interaction, item: str, price: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            msg = item
            if msg is None:
                await inter.response.send_message(f"""{inter.user}, укажите то, что Вы хотите добавить в магазин""")
            else:
                async with self.session() as session:
                    async with session.begin():
                        guild_items_shops = await session.execute(
                            select(ShopItem).where(
                                ShopItem.guild_id == inter.guild.id
                            ).order_by(ShopItem.item_id)
                        )
                        guild_items_shops = guild_items_shops.scalars().all()
                if not guild_items_shops:
                    if price is None:
                        await inter.response.send_message(f"""{inter.user}, введите цену""")
                    elif price < 1:
                        await inter.response.send_message(f"""{inter.user}, ах ты проказник! Введите цену дольше 1""")
                    elif price > 1000000:
                        await inter.response.send_message(f'{inter.user}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        async with self.session() as session:
                            async with session.begin():
                                guild_item_shop = ShopItem()
                                guild_item_shop.item_price = price
                                guild_item_shop.item_name = str(msg)
                                guild_item_shop.item_id = 1
                                session.add(guild_item_shop)
                        await inter.response.send_message('✅')
                else:
                    if price is None:
                        await inter.response.send_message(f"""{inter.user}, введите цену""")
                    elif price < 1:
                        await inter.response.send_message(f"""{inter.user}, ах ты проказник! Введите цену дольше 1""")
                    elif price > 1000000:
                        await inter.response.send_message(f'{inter.user}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        ind = max(guild_items_shops, lambda x: x.item_id).item_id
                        async with self.session() as session:
                            async with session.begin():
                                guild_item_shop = ShopItem()
                                guild_item_shop.item_price = price
                                guild_item_shop.item_name = str(msg)
                                guild_item_shop.item_id = ind + 1
                                session.add(guild_item_shop)
                        await inter.response.send_message('✅')

    @app_commands.command(name="remove-else", description="Удалить вещь из магазина")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_item_shop(self, inter: discord.Interaction, item_id: int) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            if item_id is None:
                await inter.response.send_message(
                    f"""{inter.user}, укажите номер того, что Вы хотите удалить из магазина"""
                )
            else:
                async with self.session() as session:
                    async with session.begin():
                        await session.execute(
                            delete(ShopItem).where(
                                ShopItem.item_id == item_id and ShopItem.guild_id == inter.guild.id
                            )
                        )
                await inter.response.send_message('✅')
