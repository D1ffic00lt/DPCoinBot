import discord

from discord.ext import commands
from discord.utils import get

from .helperfunction import logging
from ..database.db import Database


class Admin(commands.Cog, name='admin module', Database):
    @logging
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("server.db")
        self.bot = bot
        print("Admin connected")

    @commands.command(aliases=['give', 'award'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give(self, ctx, member: discord.Member = None, amount: int = None):
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        self.add_coins(ctx.member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        self.add_coins(ctx.member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['take'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take(self, ctx, member: discord.Member = None, amount=None):
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        if amount == "all":
                            self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        else:
                            self.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if member is None:
                    await ctx.send(f'{ctx.author}, укажите пользователя!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        if amount == "all":
                            self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        else:
                            self.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['give-role', 'award-role'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __give_role(self, ctx, role_: discord.Role = None, amount: int = None):
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
            role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if role in ctx.author.roles or ctx.author.id == 401555829620211723:
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

    @commands.command(aliases=['take-role'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __take_role(self, ctx, role_: discord.Role = None, amount=None):
        if isinstance(self.get_administrator_role_id(ctx.guild.id), bool):
            if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
                if role_ is None:
                    await ctx.send(f'{ctx.author}, укажите роль!')
                else:
                    if await self.cash_check(ctx, amount, max_cash=1000000):
                        if amount == "all":
                            for member in ctx.guild.members:
                                if get(member.roles, id=role_.id):
                                    self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                            await ctx.message.add_reaction('✅')
                        else:
                            for member in ctx.guild.members:
                                if get(member.roles, id=role_.id):
                                    self.take_coins(member.id, ctx.guild.id, amount)
                            await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас нет прав для использования этой команды")
        else:
            role = discord.utils.get(ctx.guild.roles, id=self.get_administrator_role_id(ctx.guild.id))
            if role in ctx.author.roles or ctx.author.id == 401555829620211723:
                if await self.cash_check(ctx, amount, max_cash=1000000):
                    if amount == "all":
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.take_coins(member.id, ctx.guild.id, self.get_cash(member.id, ctx.guild.id))
                        await ctx.message.add_reaction('✅')
                    else:
                        for member in ctx.guild.members:
                            if get(member.roles, id=role_.id):
                                self.take_coins(member.id, ctx.guild.id, amount)
                        await ctx.message.add_reaction('✅')
            else:
                await ctx.send("У Вас недостаточно прав для использования данной команды!")

    @commands.command(aliases=['remove-shop'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __remove_shop(self, ctx, role: discord.Role = None):
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if role is None:
                await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите удалить из магазина""")
            else:
                self.delete_from_shop(role.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
