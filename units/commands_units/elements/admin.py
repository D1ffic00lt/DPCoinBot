# -*- coding: utf-8 -*-
import logging
import discord

from typing import Union, Callable
from discord.ext import commands
from discord.utils import get

__all__ = (
    "Admin",
)

from sqlalchemy import select, delete

from sqlalchemy.ext.asyncio import AsyncSession

from database.guild.item_shops import ShopItem
from database.guild.servers import ServerSettings
from database.guild.shops import ShopRole
from database.user.users import User
from units.additions import divide_the_number


class Admin(commands.Cog):
    NAME = 'admin module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.bot = bot
        logging.info(f"Admin connected")

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
            self, ctx: Union[commands.context.Context, discord.Interaction],
            cash: Union[str, int], max_cash: int = None,
            min_cash: int = 1, check: bool = False
    ) -> bool:
        mention = ctx.author.mention if isinstance(ctx, commands.context.Context) else ctx.user.mention
        author_id = ctx.author.id if isinstance(ctx, commands.context.Context) else ctx.user.id
        if cash is None:
            message = f"{mention}, Вы не ввели сумму!"
            await ctx.send(message)
            return
        async with self.session() as session:
            user = await session.execute(
                select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
            )
            user: User = user.scalars().first()
            if not user:
                await ctx.send("no user")
                return False
        if check and cash > user.cash:
            message = f"{mention}, у Вас недостаточно средств!"
            await ctx.send(message)
        else:
            if cash == "all":
                return True
            elif max_cash is not None:
                if (int(cash) < min_cash or int(cash) > max_cash) and author_id != 401555829620211723:
                    message = f'{mention}, нельзя ввести число меньше ' \
                              f'{divide_the_number(min_cash)} и больше {divide_the_number(max_cash)}!'
                    await ctx.send(message)
                else:
                    return True
            elif max_cash is None:
                if int(cash) < min_cash and ctx.author.id != 401555829620211723:
                    message = f'{mention}, нельзя ввести число меньше {divide_the_number(min_cash)}!'
                    await ctx.send(message)
                else:
                    return True
        return False

    @commands.command(aliases=['give', 'award'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give(self, ctx: commands.context.Context, member: discord.Member = None, amount: int = None) -> None:
        administrator_role_id = self._get_administrator_role_id(ctx.guild.id)  # !
        if ctx.author.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not ctx.author.guild_permissions.administrator:
                    await ctx.reply("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(ctx.guild.roles, id=administrator_role_id)
                if role not in ctx.author.roles:
                    await ctx.reply("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if member is None:
            await ctx.reply(f'{ctx.author.mention}, укажите пользователя!')
            return
        if amount is None:
            await ctx.reply(f'{ctx.author.mention}, укажите сумму!')
            return

        if await self._check_cash(ctx, amount, max_cash=1000000):
            async with self.session() as session:
                async with session.begin():
                    user: User = await session.execute(
                        select(User).where(
                            User.guild_id == ctx.guild.id and User.user_id == member.id
                        )
                    )
                    if not user:
                        return

                    user.cash += amount
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['take'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take(
            self, ctx: commands.context.Context, member: discord.Member = None, amount: Union[str, int] = None
    ) -> None:
        administrator_role_id = self._get_administrator_role_id(ctx.guild.id)  # !
        if ctx.author.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not ctx.author.guild_permissions.administrator:
                    await ctx.reply("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(ctx.guild.roles, id=administrator_role_id)
                if role not in ctx.author.roles:
                    await ctx.reply("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if member is None:
            await ctx.reply(f'{ctx.author}, укажите пользователя!')
            return
        if amount is None:
            await ctx.reply(f'{ctx.author}, укажите сумму!')
            return
        if await self._check_cash(ctx, amount, max_cash=1000000):
            async with self.session() as session:
                async with session.begin():
                    user = await session.execute(
                        select(User).where(
                            User.guild_id == ctx.guild.id and User.user_id == member.id
                        )
                    )
                    user: User = user.scalars().first()
                    if not user:
                        return
                    if amount == "all":
                        user.cash = 0
                    else:
                        user.cash -= amount
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['give-role', 'award-role'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give_role(self, ctx: commands.context.Context, role_: discord.Role = None, amount: int = None) -> None:
        administrator_role_id = self._get_administrator_role_id(ctx.guild.id)  # !
        if ctx.author.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not ctx.author.guild_permissions.administrator:
                    await ctx.reply("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(ctx.guild.roles, id=administrator_role_id)
                if role not in ctx.author.roles:
                    await ctx.reply("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
            if role_ is None:
                await ctx.reply(f'{ctx.author}, укажите роль!')
                return
            if amount is None:
                await ctx.reply(f'{ctx.author}, укажите сумму!')
                return
            if await self._check_cash(ctx, amount, max_cash=1000000):
                for member in ctx.guild.members:
                    if get(member.roles, id=role_.id):
                        async with self.session() as session:
                            async with session.begin():
                                user = await session.execute(
                                    select(User).where(
                                        User.guild_id == ctx.guild.id and User.user_id == member.id
                                    )
                                )
                                user: User = user.scalars().first()
                                if not user:
                                    return
                                if amount == "all":
                                    user.cash = 0
                                else:
                                    user.cash -= amount
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['take-role'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take_role(
            self, ctx: commands.context.Context, role_: discord.Role = None, amount: Union[str, int] = None
    ) -> None:
        administrator_role_id = self._get_administrator_role_id(ctx.guild.id)  # !
        if ctx.author.id != 401555829620211723:
            if isinstance(administrator_role_id, bool):
                if not ctx.author.guild_permissions.administrator:
                    await ctx.reply("У Вас нет прав для использования этой команды")
                    return
            else:
                role = discord.utils.get(ctx.guild.roles, id=administrator_role_id)
                if role not in ctx.author.roles:
                    await ctx.reply("У Вас нет прав для использования этой команды", ephemeral=True)
                    return
        if role_ is None:
            await ctx.reply(f'{ctx.author}, укажите роль!')
            return
        if amount is None:
            await ctx.reply(f"{ctx.author.mention}, укажите сумму!")
            return
        if await self._check_cash(ctx, amount, max_cash=1000000):
            async with self.session() as session:
                async with session.begin():
                    for member in ctx.guild.members:
                        if get(member.roles, id=role_.id):
                            user = await session.execute(
                                select(User).where(
                                    User.guild_id == ctx.guild.id and User.user_id == member.id
                                )
                            )
                            user: User = user.scalars().first()
                            if not user:
                                continue
                            if amount == "all":
                                user.cash = 0
                            else:
                                user.cash -= amount
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['remove-shop'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_shop(self, ctx: commands.context.Context, role: discord.Role = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.reply(f"""{ctx.author}, укажите роль, которую Вы хотите удалить из магазина""")
            else:
                async with self.session() as session:
                    async with session.begin():
                        await session.execute(
                            delete(ShopRole).where(ShopRole.role_id == role.id)
                        )
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['add-shop'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_shop(self, ctx: commands.context.Context, role: discord.Role = None, cost: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.reply(f"""{ctx.author}, укажите роль, которую Вы хотите добавить в магазин""")
            else:
                if cost is None:
                    await ctx.reply(f"""{ctx.author}, введите цену роли""")
                elif cost < 1:
                    await ctx.reply(f"""{ctx.author}, ах ты проказник! Введите цену дольше 1""")
                elif cost > 100000:
                    await ctx.reply(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                else:
                    async with self.session() as session:
                        async with session.begin():
                            new_role_in_shop = ShopRole()
                            new_role_in_shop.role_id = role.id
                            new_role_in_shop.guild_id = ctx.guild.id
                            new_role_in_shop.role_cost = cost
                            session.add(new_role_in_shop)
                    await ctx.message.add_reaction('✅')

    @commands.command(aliases=['add-else'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_item_shop(self, ctx: commands.context.Context, cost: int = None, *, item) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            msg = item
            if msg is None:
                await ctx.reply(f"""{ctx.author}, укажите то, что Вы хотите добавить в магазин""")
            else:
                async with self.session() as session:
                    async with session.begin():
                        guild_items_shops = await session.execute(
                            select(ShopItem).where(
                                ShopItem.guild_id == ctx.guild.id
                            ).order_by(ShopItem.item_id)
                        )
                        guild_items_shops = guild_items_shops.scalars().all()
                if not guild_items_shops:
                    if cost is None:
                        await ctx.reply(f"""{ctx.author}, введите цену""")
                    elif cost < 1:
                        await ctx.reply(f"""{ctx.author}, ах ты проказник! Введите цену дольше 1""")
                    elif cost > 1000000:
                        await ctx.reply(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        async with self.session() as session:
                            async with session.begin():
                                guild_item_shop = ShopItem()
                                guild_item_shop.item_cost = cost
                                guild_item_shop.item_name = str(msg)
                                guild_item_shop.item_id = 1
                                session.add(guild_item_shop)
                        await ctx.message.add_reaction('✅')
                else:
                    if cost is None:
                        await ctx.reply(f"""{ctx.author}, введите цену""")
                    elif cost < 1:
                        await ctx.reply(f"""{ctx.author}, ах ты проказник! Введите цену дольше 1""")
                    elif cost > 1000000:
                        await ctx.reply(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        ind = max(guild_items_shops, lambda x: x.item_id).item_id
                        async with self.session() as session:
                            async with session.begin():
                                guild_item_shop = ShopItem()
                                guild_item_shop.item_cost = cost
                                guild_item_shop.item_name = str(msg)
                                guild_item_shop.item_id = ind + 1
                                session.add(guild_item_shop)
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=['remove-else'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_item_shop(self, ctx: commands.context.Context, item_id: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if item_id is None:
                await ctx.reply(f"""{ctx.author}, укажите номер того, что Вы хотите удалить из магазина""")
            else:
                async with self.session() as session:
                    async with session.begin():
                        await session.execute(
                            delete(ShopItem).where(
                                ShopItem.item_id == item_id and ShopItem.guild_id == ctx.guild.id
                            )
                        )
                await ctx.message.add_reaction('✅')
