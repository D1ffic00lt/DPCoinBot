import discord

from discord.ext import commands
from discord.utils import get
from dislash import slash_command, Option, OptionType

from botsections.helperfunction import logging
from database.db import Database


class AdminSlash(commands.Cog, Database, name='admin module'):
    @logging
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("../server.db")
        self.bot = bot
        self.role: discord.Role
        self.msg: str
        self.ind: int
        print("Admin Slash connected")

    @slash_command(
        name="give", description="выдать DP коины",
        options=[
            Option("member", "пользователь, которому выдадут коины", OptionType.USER),
            Option("amount", "количество коинов", OptionType.INTEGER)
        ]
    )
    async def __give_slash(
            self, ctx: commands.context.Context, member: discord.Member = None, amount: int = None
    ) -> None:
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        self.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        self.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @slash_command(
        name="take", description="списать DP коины",
        options=[
            Option("member", "пользователь, у которого спишут коины", OptionType.USER),
            Option("amount", "количество коинов", OptionType.STRING)
        ]
    )
    async def __take_slash(self, ctx: commands.context.Context, member: discord.Member = None, amount=None) -> None:
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if amount == "all":
                        self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        return
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        self.take_coins(member.id, ctx.guild.id, int(amount))
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if amount == "all":
                        self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        return
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        self.take_coins(member.id, ctx.guild.id, int(amount))
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @slash_command(
        name="give-role", description="выдать DP коины по роли",
        options=[
            Option("role", "роль", OptionType.ROLE),
            Option("amount", "количество коинов", OptionType.INTEGER)
        ]
    )
    async def __give_role_slash(
            self, ctx: commands.context.Context, role_: discord.Role = None, amount: int = None
    ) -> None:
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')

            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.add_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @slash_command(
        name="give-take", description="снять DP коины по роли",
        options=[
            Option("role", "роль", OptionType.ROLE),
            Option("amount", "количество коинов", OptionType.STRING)
        ]
    )
    async def __take_role_slash(self, ctx: commands.context.Context, role_: discord.Role = None, amount=None) -> None:
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if amount == "all":
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        await ctx.message.add_reaction('✅')
                        return
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id) and self.get_cash(member.id, ctx.guild.id) >= amount:
                                self.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            self.role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if self.role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if amount == "all":
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        await ctx.message.add_reaction('✅')
                        return
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id) and self.get_cash(member.id, ctx.guild.id) >= amount:
                                self.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @slash_command(
        name="remove-shop", description="удалить роль из магазина",
        options=[
            Option("role", "роль", OptionType.ROLE)
        ]
    )
    async def __remove_shop_slash(self, ctx: commands.context.Context, role: discord.Role = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите удалить из магазина""")
            else:
                self.delete_from_shop(role.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')

    @slash_command(
        name="add-shop", description="добавить роль в магазин",
        options=[
            Option("role", "пользователь, которому выдадут коины", OptionType.ROLE)
        ]
    )
    async def __add_shop_slash(
            self, ctx: commands.context.Context, role: discord.Role = None, cost: int = None
    ) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите добавить в магазин""")
            else:
                if cost is None:
                    await ctx.send(f"""{ctx.author}, введите цену роли""")
                elif cost < 1:
                    await ctx.send(f"""{ctx.author}, ах ты проказник! Введите цену больше 1""")
                elif cost > 100000:
                    await ctx.send(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                else:

                    self.insert_into_shop(role.id, ctx.guild.id, cost)

                    await ctx.message.add_reaction('✅')

    @slash_command(
        name="add-else", description="добавить товар в магазин",
        options=[
            Option("cash", "цена", OptionType.INTEGER),
            Option("item", "товар", OptionType.STRING)
        ]
    )
    async def __add_item_shop_slash(self, ctx: commands.context.Context, cost: int = None, *, item) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            self.msg = item
            if self.msg is None:
                await ctx.send(f"{ctx.author}, укажите то, что Вы хотите добавить в магазин")
            else:
                if self.get_from_item_shop(ctx.guild.id, "ItemID", order_by="ItemID").fetchone() is None:
                    if cost is None:
                        await ctx.send(f"{ctx.author}, введите цену")
                    elif cost < 1:
                        await ctx.send(f"{ctx.author}, ах ты проказник! Введите цену больше 1")
                    elif cost > 1000000:
                        await ctx.send(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        self.insert_into_item_shop(1, str(self.msg), ctx.guild.id, cost)
                        await ctx.message.add_reaction('✅')
                else:
                    if cost is None:
                        await ctx.send(f"""{ctx.author}, введите цену""")
                    elif cost < 1:
                        await ctx.send(f"""{ctx.author}, ах ты проказник! Введите цену больше 1""")
                    elif cost > 1000000:
                        await ctx.send(f'{ctx.author}, нельзя начислить больше 1.000.000 DP коинов!')
                    else:
                        self.ind = max(
                            [
                                i[0] for i in self.get_from_item_shop(
                                ctx.guild.id, "ItemID", order_by="ItemID"
                            ).fetchall()
                            ]
                        )
                        self.insert_into_item_shop(self.ind + 1, str(self.msg), ctx.guild.id, cost)
                        await ctx.message.add_reaction('✅')

    @slash_command(
        name="remove-else", description="добавить товар в магазин",
        options=[
            Option("товар", "товар", OptionType.STRING)
        ]
    )
    async def __remove_item_shop_slash(self, ctx: commands.context.Context, item_id: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if item_id is None:
                await ctx.send(f"""{ctx.author}, укажите номер того, что Вы хотите удалить из магазина""")
            else:
                self.delete_from_item_shop(item_id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
