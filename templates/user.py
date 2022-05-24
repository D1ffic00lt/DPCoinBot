from __future__ import annotations

import os

import discord

from discord.ext import commands

from .helperfunction import divide_the_number, create_emb, get_color, ignore_exceptions
from ..database.db import Database
from .json_ import Json


class User(commands.Cog, name='user module', Database):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.name: discord.Member
        self.color: discord.Color
        self.all_cash: int

    @commands.command(aliases=['slb'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __slb(self, ctx: commands.context.Context):
        self.all_cash = 0
        self.color = get_color(ctx.author.roles)
        if not os.path.exists(".json/develop_get.json"):
            Json("develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json("develop_get.json").json_load()
        for row in self.get_from_user(ctx.guild.id, "Name", "Cash", "ID", order_by="Cash"):
            for member in ctx.guild.members:
                if str(member) == row[0]:
                    self.name = member
                    break
            if self.name is not None and not self.name.bot:
                for member in ctx.guild.members:
                    if self.name.id == member.id:
                        if self.name.id == 401555829620211723 and \
                                ctx.guild.id == 493970394374471680 and self.js["slb"] is False:
                            pass
                        else:
                            self.all_cash += row[1]
                        break
        await ctx.send(
            embed=create_emb(
                title="Общий баланс сервера:",
                color=self.color,
                args=[
                    {
                        "name": f"Баланс сервера {ctx.guild}",
                        "value": f"Общий баланс сервера {ctx.guild} составляет "
                                 f"{divide_the_number(self.all_cash)} "
                                 f" DP коинов",
                        "inline": False
                    }
                ]
            )
        )

    @commands.command(aliases=["leader", "lb"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __lb(self, ctx: commands.context.Context, type_: str = None):
        self.counter = 0
        self.name: discord.Member
        self.index = 0
        if not os.path.exists(".json/develop_get.json"):
            Json("develop_get.json").json_dump({"lb": True, "slb": True})
            self.js = {"lb": True, "slb": True}
        else:
            self.js = Json("develop_get.json").json_load()
        if type_ is None:
            self.emb = discord.Embed(title="Топ 10 сервера")
            for row in self.get_from_user(ctx.guild.id, "Name", "Cash", "Lvl", "ID", order_by="Cash"):
                if self.index == 10:
                    break
                for member in ctx.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in ctx.guild.members:
                        if member.id == row[3]:
                            if self.name.id == 401555829620211723 and ctx.guild.id == 493970394374471680 \
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

            await ctx.send(embed=self.emb)
        elif type_ == "chat":
            self.emb = discord.Embed(title="Топ 10 сервера по левелу")
            for row in self.get_from_user(ctx.guild.id, "Name", "ChatLevel", "ID", "Xp", order_by="Xp"):
                if self.index == 10:
                    break
                for member in ctx.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in ctx.guild.members:
                        if member.id == row[2]:
                            self.counter += 1
                            self.emb.add_field(
                                name=f'# {self.counter} | `{row[0]}` | chat lvl `{row[1]}`',
                                value=f'xp: **{divide_the_number(row[3])}**',
                                inline=False
                            )
                            self.index += 1
                            break

            await ctx.send(embed=self.emb)
        elif type_ == "voice":
            self.emb = discord.Embed(title="Топ 10 сервера по времени в голосовых каналах")
            for row in self.get_from_user(
                    ctx.guild.id,
                    "Name",
                    "MinutesInVoiceChannels",
                    "ID",
                    order_by="MinutesInVoiceChannels"
            ):
                if self.index == 10:
                    break
                for member in ctx.guild.members:
                    if str(member) == row[0]:
                        self.name = member
                        break

                if not self.name.bot:
                    for member in ctx.guild.members:
                        if member.id == row[2]:
                            self.counter += 1
                            self.emb.add_field(
                                name=f'# {self.counter} | `{row[0]}`',
                                value=f'**{divide_the_number(row[1])} минут ({divide_the_number(row[1] / 60)} часов)**',
                                inline=False
                            )
                            self.index += 1
                            break

            await ctx.send(embed=self.emb)

    @ignore_exceptions  # т.к member может не быть на сервере, но упомянут через <@id>
    @commands.command(aliases=["balance", "cash"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __balance(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None
    ):
        if member is None:
            await ctx.send(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя `{ctx.author}` составляет "
                                f"`{divide_the_number(self.get_cash(ctx.author.id, ctx.guild.id))}` DP коинов"
                )
            )
        else:
            await ctx.send(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя `{member}` составляет "
                                f"`{divide_the_number(self.get_cash(member.id, ctx.guild.id))}` DP коинов"
                )
            )

    @commands.command(aliases=["bank"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __bank(
            self,
            ctx: commands.context.Context,
            action: str = None,
            cash: int | str = None
    ) -> None:
        if action is None:
            await ctx.send(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя `{ctx.author}` составляет "
                                f"`{divide_the_number(self.get_cash(ctx.author.id, ctx.guild.id))}` DP коинов\n\n"
                                f"Баланс в банке составляет"
                                f"`{divide_the_number(self.get_cash(ctx.author.id, ctx.guild.id, bank=True))}` "
                                f"DP коинов\n\nВсего коинов - `"
                                f"""{divide_the_number(
                                    self.get_cash(
                                        ctx.author.id, 
                                        ctx.guild.id
                                    )
                                ) + divide_the_number(
                                    self.get_cash(
                                        ctx.author.id, 
                                        ctx.guild.id, 
                                        bank=True
                                    )
                                )}`"""
                )
            )
        elif action == "add":
            if await self.cash_check(ctx, cash):
                self.add_coins_to_the_bank(ctx.author.id, ctx.guild.id, cash)
                await ctx.message.add_reaction('✅')

        elif action == "take":
            if cash == "all":
                self.take_coins_from_the_bank(ctx.author.id, ctx.guild.id, "all")
            else:
                if cash is None:
                    await ctx.send(f"""{ctx.author.mention}, Вы не ввели сумму!""")
                elif cash > self.get_cash(ctx.author.id, ctx.guild.id, bank=True):
                    await ctx.send(f"""{ctx.author.mention}, у Вас недостаточно средств!""")
                if await self.cash_check(ctx, cash):
                    self.take_coins_from_the_bank(ctx.author.id, ctx.guild.id, cash)
                    await ctx.message.add_reaction('✅')
