import discord

from discord.ext import commands
from discord.utils import get

from botsections.functions.helperfunction import logging
from database.db import Database

__all__ = (
    "Admin",
)


class Admin(commands.Cog):
    NAME = 'admin module'

    __slots__ = (
        "db", "bot", "role", "msg", "ind", "logs"
    )

    @logging
    def __init__(self, bot: commands.Bot, db: Database, logs, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db: Database = db
        self.bot = bot
        self.role: discord.Role
        self.msg: str
        self.ind: int
        self.logs = logs
        print("Admin connected")

    @commands.command(aliases=['give', 'award'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give(self, ctx: commands.context.Context, member: discord.Member = None, amount: int = None) -> None:
        if isinstance(self.db.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        self.db.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.db.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        self.db.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['take'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take(self, ctx: commands.context.Context, member: discord.Member = None, amount=None) -> None:
        if isinstance(self.db.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        if amount == "all":
                            self.db.take_coins(member.id, ctx.guild.id, self.db.get_cash(member.id, ctx.guild.id))
                        else:
                            self.db.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.db.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        if amount == "all":
                            self.db.take_coins(member.id, ctx.guild.id, self.db.get_cash(member.id, ctx.guild.id))
                        else:
                            self.db.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['give-role', 'award-role'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give_role(self, ctx: commands.context.Context, role_: discord.Role = None, amount: int = None) -> None:
        if isinstance(self.db.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.db.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')

            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.db.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.db.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['take-role'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take_role(self, ctx: commands.context.Context, role_: discord.Role = None, amount=None) -> None:
        if isinstance(self.db.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if await self.db.cash_check(ctx, amount, max_cash=1000000):
                        if amount == "all":
                            for member in ctx.guild.members:
                                if get(member.roles, id=role_.id):
                                    self.db.take_coins(
                                        member.id,
                                        ctx.guild.id,
                                        self.db.get_cash(member.id, ctx.guild.id)
                                    )
                            await ctx.message.add_reaction('✅')
                        else:
                            for member in ctx.guild.members:
                                if get(member.roles, id=role_.id):
                                    self.db.take_coins(member.id, ctx.guild.id, amount)
                            await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.db.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if await self.db.cash_check(ctx, amount, max_cash=1000000):
                    if amount == "all":
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.db.take_coins(member.id, ctx.guild.id, self.db.get_cash(member.id, ctx.guild.id))
                        await ctx.message.add_reaction('✅')
                    else:
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.db.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['remove-shop'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_shop(self, ctx: commands.context.Context, role: discord.Role = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите удалить из магазина""")
            else:
                self.db.delete_from_shop(role.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['add-shop'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_shop(self, ctx: commands.context.Context, role: discord.Role = None, cost: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите добавить в магазин""")
            else:
                if cost is None:
                    await ctx.send(f"""{ctx.author}, введите цену роли""")
                elif cost < 1:
                    await ctx.send(f"""{ctx.author}, ах ты проказник! Введите цену дольше 1""")
                elif cost > 100000:
                    await ctx.send(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                else:

                    self.db.insert_into_shop(role.id, ctx.guild.id, cost)

                    await ctx.message.add_reaction('✅')

    @commands.command(aliases=['add-else'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __add_item_shop(self, ctx: commands.context.Context, cost: int = None, *, item) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            self.msg = item
            if self.msg is None:
                await ctx.send(f"""{ctx.author}, укажите то, что Вы хотите добавить в магазин""")
            else:
                if self.db.get_from_item_shop(ctx.guild.id, "ItemID", order_by="ItemID").fetchone() is None:
                    if cost is None:
                        await ctx.send(f"""{ctx.author}, введите цену""")
                    elif cost < 1:
                        await ctx.send(f"""{ctx.author}, ах ты проказник! Введите цену дольше 1""")
                    elif cost > 1000000:
                        await ctx.send(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        self.db.insert_into_item_shop(1, str(self.msg), ctx.guild.id, cost)
                        await ctx.message.add_reaction('✅')
                else:
                    if cost is None:
                        await ctx.send(f"""{ctx.author}, введите цену""")
                    elif cost < 1:
                        await ctx.send(f"""{ctx.author}, ах ты проказник! Введите цену дольше 1""")
                    elif cost > 1000000:
                        await ctx.send(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        self.ind = max(
                            [
                                i[0] for i in self.db.get_from_item_shop(
                                    ctx.guild.id,
                                    "ItemID",
                                    order_by="ItemID"
                                ).fetchall()
                            ]
                        )
                        self.db.insert_into_item_shop(self.ind + 1, str(self.msg), ctx.guild.id, cost)
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=['remove-else'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_item_shop(self, ctx: commands.context.Context, item_id: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if item_id is None:
                await ctx.send(f"""{ctx.author}, укажите номер того, что Вы хотите удалить из магазина""")
            else:
                self.db.delete_from_item_shop(item_id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
