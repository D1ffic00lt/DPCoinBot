from __future__ import annotations

import os
import discord

from discord.ext import commands

from .helperfunction import divide_the_number, create_emb, get_color, ignore_exceptions
from ..database.db import Database
from .json_ import Json
from .texts import *


class User(commands.Cog, name='user module', Database):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.name: discord.Member
        self.color: discord.Color
        self.all_cash: int
        self.level: int
        self.counter: int = 0
        self.index: int = 0

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

    @commands.command(aliases=['levels'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __levels_shop(self, ctx: commands.context.Context):
        await ctx.send(embed=create_emb(
            title="Всё о левелах!",
            args=[
                {
                    "name": f'Level 1',
                    "value": levels["level1"],
                    "inline": False
                },
                {
                    "name": f'Level 2',
                    "value": levels["level2"],
                    "inline": False
                },
                {
                    "name": f'Level 3',
                    "value": levels["level3"],
                    "inline": False
                },
                {
                    "name": f'Level 4',
                    "value": levels["level4"],
                    "inline": False
                },
                {
                    "name": f'Level 5',
                    "value": levels["level5"],
                    "inline": False
                },
                {
                    "name": f'**Как поднять левел?**',
                    "value": levels["LevelUp"],
                    "inline": False
                }
            ]
        )
        )

    @commands.command(aliases=['lvl_up'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __level_up(self, ctx: commands.context.Context):
        self.level = self.get_level(ctx.author.id, ctx.guild.id)
        if self.level == 5:
            await ctx.send("У Вас максимальный левел!")
        elif self.level == 1:
            if 50000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 50000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
        elif self.level == 2:
            if 100000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 100000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
        elif self.level == 3:
            if 200000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 200000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')
        elif self.level == 4:
            if 400000 > self.get_cash(ctx.author.id, ctx.guild.id):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(ctx.author.id, ctx.guild.id, 400000)
                self.add_level(ctx.author.id, ctx.guild.id)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['shop'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __shop(self, ctx: commands.context.Context):
        self.emb = discord.Embed(title="Магазин ролей")
        for row in self.get_from_shop(ctx.guild.id, "RoleID", "RoleCost", order_by="RoleCost"):
            if ctx.guild.get_role(row[0]) is not None:
                self.emb.add_field(
                    name=f'Роль {ctx.guild.get_role(row[0]).mention}',
                    value=f'Стоимость: **{row[1]} DP коинов**',
                    inline=False
                )
        self.emb.add_field(name="**Как купить роль?**",
                           value=f'''```diff\n- {settings["prefix"]}buy <Упоминание роли>\n```''')
        self.get_from_item_shop(ctx.guild.id, "ItemID", "ItemName", "ItemCost", order_by="Cost")
        if self.get_from_item_shop(
                ctx.guild.id,
                "ItemID",
                "ItemName",
                "ItemCost",
                order_by="Cost"
        ).fetchone() is not None:
            self.emb.add_field(name='**Другое:**\n', value="Сообщение о покупке придет администрации!", inline=False)
            for row in self.get_from_item_shop(ctx.guild.id, "ItemID", "ItemName", "ItemCost", order_by="Cost"):
                self.emb.add_field(
                    name=f'**{row[1]}**',
                    value=f'Стоимость: **{row[2]} DP коинов**\n'
                          f'Чтобы купить {settings["prefix"]}buy_item {row[0]}',
                    inline=False
                )

        self.emb.add_field(
            name="**Чтобы купить роль:**",
            value=f"```diff\n- {settings['prefix']}buy @роль, которую Вы хотите купить\n```")
        await ctx.send(embed=self.emb)

    @commands.command(aliases=["buy_item"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy_item(self, ctx: commands.context.Context, item: int = None):
        if item is None:
            await ctx.send(f"""{ctx.author}, укажите то, что Вы хотите приобрести""")
        else:
            self.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="Cost")
            if self.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="Cost").fetchone() is None:
                await ctx.send(f"""{ctx.author}, такого товара не существует!""")
            elif self.get_item_from_item_shop(ctx.guild.id, item, "*", order_by="Cost").fetchone()[0] > self.get_cash(
                    ctx.author.id, ctx.guild.id
            ):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств!""")
            else:
                self.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.get_item_from_item_shop(ctx.guild.id, item, "Cost", order_by="Cost")
                )
                await ctx.message.add_reaction('✅')
                channel = self.bot.get_channel(self.get_from_server(ctx.guild.id, "ChannelID"))
                await channel.send(f"Покупка {ctx.author.mention} товар номер {item}")
                await ctx.send("Администрация скоро выдаст Вам товар")

    @commands.command(aliases=["buy", "buy-role"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy(self, ctx: commands.context.Context, role: discord.Role = None):
        if role is None:
            await ctx.send(f"""{ctx.author}, укажите роль, которую Вы хотите приобрести""")
        else:
            if role in ctx.author.roles:
                await ctx.send(f"""{ctx.author}, у Вас уже есть эта роль!""")
            elif self.get_from_shop(ctx.author.id, ctx.guild.id, "Cost", order_by="Cost").fetchone() is None:
                pass
            elif self.get_from_shop(ctx.author.id, ctx.guild.id, "Cost", order_by="Cost").fetchone()[0] > self.get_cash(
                    ctx.author.id, ctx.guild.id
            ):
                await ctx.send(f"""{ctx.author}, у Вас недостаточно средств для покупки этой роли!""")
            else:
                await ctx.author.add_roles(role)
                self.take_coins(
                    ctx.author.id,
                    ctx.guild.id,
                    self.get_from_shop(
                        ctx.guild.id,
                        "RoleCost",
                        order_by="RoleCost",
                        role_id=role.id
                    )
                )
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["send"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None,
            cash: int = None
    ):
        if member is None:
            await ctx.send(f"""{ctx.author}, укажите пользователя, которому Вы хотите перевести коины""")
        else:
            if await self.cash_check(ctx, cash, check=True):
                if member.id == ctx.author.id:
                    await ctx.send(f"""{ctx.author}, Вы не можете перевести деньги себе""")
                else:
                    self.take_coins(ctx.author.id, ctx.guild.id, cash)
                    self.add_coins(member.id, ctx.guild.id, cash)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["+rep"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __good_rep(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None
    ):
        if member is None:
            await ctx.send(f"{ctx.author}, Вы не указали пользователя!")
        else:
            if member.id == ctx.author.id:
                await ctx.send(f"{ctx.author}, Вы не можете повысить репутацию самому себе")
            else:
                self.add_reputation(ctx.author.id, ctx.guild.id, 1)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["-rep"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __bad_rep(
            self,
            ctx: commands.context.Context,
            member: discord.Member = None
    ):
        if member is None:
            await ctx.send(f"{ctx.author}, Вы не указали пользователя!")
        else:
            if member.id == ctx.author.id:
                await ctx.send(f"{ctx.author}, Вы не можете понизить репутацию самому себе")
            else:
                self.add_reputation(ctx.author.id, ctx.guild.id, -1)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=["rep"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __rep(self, ctx):
        self.emb = discord.Embed(title="Топ 10 сервера")
        self.counter = 0
        for row in self.get_from_user(ctx.guild.id, "Name", "Reputation", order_by="Reputation", limit=10):
            self.counter += 1
            self.emb.add_field(
                name=f'# {self.counter} | `{row[0]}`',
                value=f'Репутация: {row[1]}',
                inline=False
            )
        await ctx.send(embed=self.emb)

    # @commands.command(aliases=["stats"])
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def __stats(self, ctx, member: discord.Member = None):
    #     if member is None:
    #         coinflips = cursor.execute("SELECT coinflips FROM users WHERE id = ? AND server_id = ?",
    #                                    [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         cf_wins = cursor.execute("SELECT cf_wins FROM users WHERE id = ? AND server_id = ?",
    #                                  [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         cf_loses = cursor.execute("SELECT cf_loses FROM users WHERE id = ? AND server_id = ?",
    #                                   [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         rust_casinos = cursor.execute("SELECT rust_casinos FROM users WHERE id = ? AND server_id = ?",
    #                                       [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         rc_wins = cursor.execute("SELECT rc_wins FROM users WHERE id = ? AND server_id = ?",
    #                                  [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         rc_loses = cursor.execute("SELECT rc_loses FROM users WHERE id = ? AND server_id = ?",
    #                                   [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         rolls = cursor.execute("SELECT rolls FROM users WHERE id = ? AND server_id = ?",
    #                                [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         r_wins = cursor.execute("SELECT r_wins FROM users WHERE id = ? AND server_id = ?",
    #                                 [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         r_loses = cursor.execute("SELECT r_loses FROM users WHERE id = ? AND server_id = ?",
    #                                  [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         fails = cursor.execute("SELECT fails FROM users WHERE id = ? AND server_id = ?",
    #                                [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         f_wins = cursor.execute("SELECT f_wins FROM users WHERE id = ? AND server_id = ?",
    #                                 [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         f_loses = cursor.execute("SELECT f_loses FROM users WHERE id = ? AND server_id = ?",
    #                                  [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         ssss = cursor.execute("SELECT ssss FROM users WHERE id = ? AND server_id = ?",
    #                               [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         s_wins = cursor.execute("SELECT s_wins FROM users WHERE id = ? AND server_id = ?",
    #                                 [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         s_loses = cursor.execute("SELECT s_loses FROM users WHERE id = ? AND server_id = ?",
    #                                  [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         all_wins = cursor.execute("SELECT all_wins FROM users WHERE id = ? AND server_id = ?",
    #                                   [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         all_loses = cursor.execute("SELECT all_loses FROM users WHERE id = ? AND server_id = ?",
    #                                    [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         count = cursor.execute("SELECT count FROM users WHERE id = ? AND server_id = ?",
    #                                [ctx.author.id, ctx.guild.id]).fetchone()[0]
    #         chat_lvl = cursor.execute(
    #             "SELECT chat_lvl FROM users WHERE id = ? AND server_id = ?",
    #             [ctx.author.id, ctx.author.guild.id]).fetchone()[0]
    #         xp = cursor.execute(
    #             "SELECT xp FROM users WHERE id = ? AND server_id = ?",
    #             [ctx.author.id, ctx.author.guild.id]).fetchone()[0]
    #         all_xp = xp
    #         xp = cursor.execute("SELECT xp FROM levels WHERE level = ?", [chat_lvl + 1]).fetchone()[0] - xp
    #         emb = discord.Embed(title="Статистика {}".format(ctx.author))
    #         emb.add_field(name='Coinflips - {}'.format(coinflips),
    #                       value='Wins - {}\n Loses - {}'.format(cf_wins, cf_loses))
    #         emb.add_field(name='Rust casinos - {}'.format(rust_casinos),
    #                       value='Wins - {}\n Loses - {}'.format(rc_wins, rc_loses))
    #         emb.add_field(name='Rolls - {}'.format(rolls),
    #                       value='Wins - {}\n Loses - {}'.format(r_wins, r_loses))
    #         emb.add_field(name='Fails - {}'.format(fails),
    #                       value='Wins - {}\n Loses - {}'.format(f_wins, f_loses))
    #         emb.add_field(name='777s - {}'.format(ssss),
    #                       value='Wins - {}\n Loses - {}'.format(s_wins, s_loses))
    #         emb.add_field(name='Побед/Поражений всего'.format(ssss),
    #                       value='Wins - {}\n Loses - {}'.format(all_wins, all_loses))
    #         emb.add_field(name='Выиграно всего'.format(ssss),
    #                       value=razr(count))
    #         emb.add_field(name='Минут в голосовых чатах'.format(ssss),
    #                       value="{} минут в голосовых чатах".format(
    #                           cursor.execute("SELECT voice_minutes FROM users WHERE id = ? AND server_id = ?",
    #                                          [ctx.author.id, ctx.guild.id]).fetchone()[0]))
    #         emb.add_field(name='Сообщений в чате'.format(ssss),
    #                       value="{} сообщений в чате".format(
    #                           cursor.execute("SELECT messages FROM users WHERE id = ? AND server_id = ?",
    #                                          [ctx.author.id, ctx.guild.id]).fetchone()[0]))
    #         emb.add_field(name='{} левел'.format(chat_lvl),
    #                       value="{} опыта до следующего левела, {} опыта всего".format(xp, all_xp))
    #         await ctx.send(embed=emb)
    #     else:
    #         coinflips = cursor.execute("SELECT coinflips FROM users WHERE id = ? AND server_id = ?",
    #                                    [member.id, member.guild.id]).fetchone()[0]
    #         cf_wins = cursor.execute("SELECT cf_wins FROM users WHERE id = ? AND server_id = ?",
    #                                  [member.id, member.guild.id]).fetchone()[0]
    #         cf_loses = cursor.execute("SELECT cf_loses FROM users WHERE id = ? AND server_id = ?",
    #                                   [member.id, member.guild.id]).fetchone()[0]
    #         rust_casinos = cursor.execute("SELECT rust_casinos FROM users WHERE id = ? AND server_id = ?",
    #                                       [member.id, member.guild.id]).fetchone()[0]
    #         rc_wins = cursor.execute("SELECT rc_wins FROM users WHERE id = ? AND server_id = ?",
    #                                  [member.id, member.guild.id]).fetchone()[0]
    #         rc_loses = cursor.execute("SELECT rc_loses FROM users WHERE id = ? AND server_id = ?",
    #                                   [member.id, member.guild.id]).fetchone()[0]
    #         rolls = cursor.execute("SELECT rolls FROM users WHERE id = ? AND server_id = ?",
    #                                [member.id, member.guild.id]).fetchone()[0]
    #         r_wins = cursor.execute("SELECT r_wins FROM users WHERE id = ? AND server_id = ?",
    #                                 [member.id, member.guild.id]).fetchone()[0]
    #         r_loses = cursor.execute("SELECT r_loses FROM users WHERE id = ? AND server_id = ?",
    #                                  [member.id, member.guild.id]).fetchone()[0]
    #         fails = cursor.execute("SELECT fails FROM users WHERE id = ? AND server_id = ?",
    #                                [member.id, member.guild.id]).fetchone()[0]
    #         f_wins = cursor.execute("SELECT f_wins FROM users WHERE id = ? AND server_id = ?",
    #                                 [member.id, member.guild.id]).fetchone()[0]
    #         f_loses = cursor.execute("SELECT f_loses FROM users WHERE id = ? AND server_id = ?",
    #                                  [member.id, member.guild.id]).fetchone()[0]
    #         ssss = cursor.execute("SELECT ssss FROM users WHERE id = ? AND server_id = ?",
    #                               [member.id, member.guild.id]).fetchone()[0]
    #         s_wins = cursor.execute("SELECT s_wins FROM users WHERE id = ? AND server_id = ?",
    #                                 [member.id, member.guild.id]).fetchone()[0]
    #         s_loses = cursor.execute("SELECT s_loses FROM users WHERE id = ? AND server_id = ?",
    #                                  [member.id, member.guild.id]).fetchone()[0]
    #         all_wins = cursor.execute("SELECT all_wins FROM users WHERE id = ? AND server_id = ?",
    #                                   [member.id, member.guild.id]).fetchone()[0]
    #         all_loses = cursor.execute("SELECT all_loses FROM users WHERE id = ? AND server_id = ?",
    #                                    [member.id, member.guild.id]).fetchone()[0]
    #         count = cursor.execute("SELECT count FROM users WHERE id = ? AND server_id = ?",
    #                                [member.id, member.guild.id]).fetchone()[0]
    #         chat_lvl = cursor.execute(
    #             "SELECT chat_lvl FROM users WHERE id = ? AND server_id = ?",
    #             [member.id, member.guild.id]).fetchone()[0]
    #         xp = cursor.execute(
    #             "SELECT xp FROM users WHERE id = ? AND server_id = ?",
    #             [member.id, member.guild.id]).fetchone()[0]
    #         all_xp = xp
    #         xp = cursor.execute("SELECT xp FROM levels WHERE level = ?", [chat_lvl + 1]).fetchone()[0] - xp
    #         emb = discord.Embed(title="Статистика {}".format(member))
    #         emb.add_field(name='Coinflips - {}'.format(coinflips),
    #                       value='Wins - {}\n Loses - {}'.format(cf_wins, cf_loses))
    #         emb.add_field(name='Rust casinos - {}'.format(rust_casinos),
    #                       value='Wins - {}\n Loses - {}'.format(rc_wins, rc_loses))
    #         emb.add_field(name='Rolls - {}'.format(rolls),
    #                       value='Wins - {}\n Loses - {}'.format(r_wins, r_loses))
    #         emb.add_field(name='Fails - {}'.format(fails),
    #                       value='Wins - {}\n Loses - {}'.format(f_wins, f_loses))
    #         emb.add_field(name='777s - {}'.format(ssss),
    #                       value='Wins - {}\n Loses - {}'.format(s_wins, s_loses))
    #         emb.add_field(name='Побед/Поражений всего'.format(ssss),
    #                       value='Wins - {}\n Loses - {}'.format(all_wins, all_loses))
    #         emb.add_field(name='Выиграно всего'.format(ssss),
    #                       value=razr(count))
    #         emb.add_field(name='Минут в голосовых чатах'.format(ssss),
    #                       value="{} минут в голосовых чатах".format(
    #                           cursor.execute("SELECT voice_minutes FROM users WHERE id = ? AND server_id = ?",
    #                                          [member.id, member.guild.id]).fetchone()[0]))
    #         emb.add_field(name='Сообщений в чате'.format(ssss),
    #                       value="{} сообщений в чате".format(
    #                           cursor.execute("SELECT messages FROM users WHERE id = ? AND server_id = ?",
    #                                          [member.id, member.guild.id]).fetchone()[0]))
    #         emb.add_field(name='{} левел'.format(chat_lvl),
    #                       value="{} опыта до следующего левела, {} опыта всего".format(xp, all_xp))
    #         await ctx.send(embed=emb)