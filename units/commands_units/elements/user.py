# -*- coding: utf-8 -*-
import os
import discord
import logging

from discord.ext import commands
from typing import Union, Callable

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from database.bot.levels import Level
from database.guild.item_shops import ShopItem
from database.guild.promo_codes import PromoCode
from database.guild.servers import ServerSettings
from database.guild.shops import ShopRole
from units.additions import (
    divide_the_number, create_emb,
    get_color,
    get_promo_code
)
from units.json_logging import Json
from units.gpt.gpt3 import GTP3Model
from units.card_generator import CardGenerator
from database.user.users import User as DBUser
from config import PREFIX

__all__ = (
    "User",
)


class User(commands.Cog):
    NAME = 'user module'

    def __init__(self, bot: commands.Bot, session, gpt_token: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.gpt_token = gpt_token
        server: Union[discord.Guild, type(None)]
        self.bot: commands.Bot = bot
        self.gpt_users: dict[int, GTP3Model] = {}
        logging.info(f"User connected")

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
                select(User).where(DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id)
            )
            user: DBUser = user.scalars().first()
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

    @commands.command(aliases=["slb"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __slb(self, ctx: commands.context.Context) -> None:
        all_cash = 0
        color = get_color(ctx.author.roles)
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            js = {"lb": True, "slb": True}
        else:
            js = Json(".json/develop_get.json").json_load()
        async with self.session() as session:
            async with session.begin():
                users = await session.execute(
                    select(DBUser).where(DBUser.user_id == ctx.guild.id).order_by(DBUser.cash)
                )
                users = users.scalars()

        for user in users:
            name = self.bot.get_user(user.user_id)
            if name is not None and not name.bot:
                for member in ctx.guild.members:
                    if name.id == member.id:
                        if name.id == 401555829620211723 and \
                                ctx.guild.id == 493970394374471680 and js["slb"] is False:
                            pass
                        else:
                            all_cash += user.cash
                        break
        await ctx.reply(
            embed=create_emb(
                title="Общий баланс сервера:",
                color=color,
                args=[
                    {
                        "name": f"Баланс сервера {ctx.guild}",
                        "value": f"Общий баланс сервера {ctx.guild} составляет "
                                 f"{divide_the_number(all_cash)} "
                                 f" DP коинов",
                        "inline": False
                    }
                ]
            )
        )

    @commands.command(aliases=["leader", "lb"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __lb(self, ctx: commands.context.Context, type_: str = None) -> None:
        counter = 0
        index = 0
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            js = {"lb": True, "slb": True}
        else:
            js = Json(".json/develop_get.json").json_load()
        if type_ is None:
            emb = discord.Embed(title="Топ 10 сервера")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.user_id == ctx.guild.id
                        ).order_by(DBUser.cash).limit(10)
                    )
                    users = users.scalars()
            for user in users:
                user: DBUser = user
                if index == 10:
                    break
                name = self.bot.get_user(user.user_id)

                if not name.bot:
                    if name.id == 401555829620211723 and ctx.guild.id == 493970394374471680 \
                            and js["lb"] is False:
                        continue
                    else:
                        counter += 1
                        emb.add_field(
                            name=f'# {counter} | `{name.name}` | lvl `{user.users_stats.chat_lvl}`',
                            value=f'Баланс: {divide_the_number(user.cash)}',
                            inline=False
                        )
                        index += 1
                    break

            await ctx.reply(embed=emb)
        elif type_ == "chat":
            emb = discord.Embed(title="Топ 10 сервера по левелу")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == ctx.guild.id
                        ).order_by(DBUser.users_stats.xp).limit(10)
                    )
                    users = users.scalars()
            for user in users:
                if index == 10:
                    break
                name = self.bot.get_user(user.user_id)

                if not name.bot:
                    counter += 1
                    emb.add_field(
                        name=f'# {counter} | `{name.name}` | chat lvl `{user.users_stats.chat_lvl}`',
                        value=f'xp: **{divide_the_number(user.users_stats.xp)}**',
                        inline=False
                    )
                    index += 1

            await ctx.reply(embed=emb)
        elif type_ == "voice":
            emb = discord.Embed(title="Топ 10 сервера по времени в голосовых каналах")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == ctx.guild.id).order_by(
                                DBUser.users_stats.minutes_in_voice_channels
                        ).limit(10)
                    )
                    users = users.scalars()
            for user in users:
                if index == 10:
                    break
                name = self.bot.get_user(user.user_id)

                if not name.bot:
                    counter += 1
                    emb.add_field(
                        name=f'# {counter} | `{name.name}`',
                        value=f'**{divide_the_number(user.users_stats.minutes_in_voice_channels)} минут '
                              f'({divide_the_number(user.users_stats.minutes_in_voice_channels / 60)} часов)**',
                        inline=False
                    )
                    index += 1

            await ctx.reply(embed=emb)
        elif type_ == "rep":
            emb = discord.Embed(title="Топ 10 сервера")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == ctx.guild.id).order_by(
                                DBUser.users_stats.reputation
                        ).limit(10)
                    )
                    users = users.scalars()
            counter = 0
            for user in users:
                counter += 1
                emb.add_field(
                    name=f'# {counter} | `{self.bot.get_user(user.user_id).name}`',
                    value=f'Репутация: {user.users_stats.reputation}',
                    inline=False
                )
            await ctx.reply(embed=emb)

    @commands.command(aliases=["cash"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __balance(
            self, ctx: commands.context.Context,
            member: discord.Member = None
    ) -> None:
        if member is None:
            try:
                async with self.session() as session:
                    async with session.begin():
                        user = await session.execute(
                            select(User).where(
                                DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                            )
                        )
                user = user.scalars().first()
                await ctx.reply(
                    embed=create_emb(
                        title="Баланс",
                        description=f"Баланс пользователя ```{ctx.author}``` составляет "
                                    f"```{divide_the_number(user.cash)}``` "
                                    f"DP коинов"
                    )
                )
            except TypeError:
                logging.error(f"TypeError: user.py 226 cash")
        else:
            async with self.session() as session:
                async with session.begin():
                    user = await session.execute(
                        select(User).where(
                            DBUser.user_id == member.id and DBUser.guild_id == ctx.guild.id
                        )
                    )
            user = user.scalars().first()
            await ctx.reply(
                embed=create_emb(
                    title="Баланс",
                    description=f"Баланс пользователя ```{member}``` составляет "
                                f"```{divide_the_number(user.cash)}``` DP коинов"
                )
            )

    @commands.command(aliases=["bank"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __bank(
            self, ctx: commands.context.Context,
            action: str = None, cash: Union[int, str] = None
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                if action is None:
                    all_cash = user.cash + user.cash_in_bank
                    await ctx.reply(
                        embed=create_emb(
                            title="Баланс",
                            description=f"Баланс пользователя ```{ctx.author}``` составляет "
                                        f"```{divide_the_number(user.cash)}```"
                                        f" DP коинов\n\nБаланс в банке составляет"
                                        f"```{divide_the_number(user.cash_in_bank)}``` "
                                        f"DP коинов\n\nВсего коинов - `"
                                        f"{divide_the_number(all_cash)}"
                        )
                    )
                elif action == "add":
                    if await self._check_cash(ctx, cash):
                        user.cash_in_bank += cash
                        await ctx.message.add_reaction('✅')

                elif action == "take":
                    if cash == "all":
                        user.cash += user.cash_in_bank
                        user.cash_in_bank = 0
                    else:
                        if cash is None:
                            await ctx.reply(f"""{ctx.author.mention}, Вы не ввели сумму!""")
                        elif cash > user.cash_in_bank:
                            await ctx.reply(f"""{ctx.author.mention}, у Вас недостаточно средств!""")
                        if await self._check_cash(ctx, cash):
                            user.cash += cash
                            user.cash_in_bank -= cash
                            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['shop'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __shop(self, ctx: commands.context.Context):
        emb = discord.Embed(title="Магазин ролей")
        async with self.session() as session:
            async with session.begin():
                shops = await session.execute(
                    select(ShopRole).where(ShopRole.guild_id == ctx.guild.id).order_by(ShopRole.role_cost)
                )
                shops = shops.scalars()
                item_shops = await session.execute(
                    select(ShopItem).where(ShopItem.guild_id == ctx.guild.id).order_by(ShopItem.item_cost)
                )
                item_shops = item_shops.scalars()
        for role in shops:
            if ctx.guild.get_role(role.role_id) is not None:
                emb.add_field(
                    name=f'Роль {ctx.guild.get_role(role.role_id).mention}',
                    value=f'Стоимость: **{role.role_cost} DP коинов**',
                    inline=False
                )
        emb.add_field(name="**Как купить роль?**",
                           value=f'''```diff\n- {PREFIX}buy <Упоминание роли>\n```''')
        if item_shops is not None:
            emb.add_field(name='**Другое:**\n', value="Сообщение о покупке придет администрации!", inline=False)
            for item in item_shops:
                item: ShopItem = item
                emb.add_field(
                    name=f'**{item.item_name}**',
                    value=f'Стоимость: **{item.item_cost} DP коинов**\n'
                          f'Чтобы купить {PREFIX}buy_item {item.item_id}',
                    inline=False
                )

        emb.add_field(
            name="**Чтобы купить роль:**",
            value=f"```diff\n- {PREFIX}buy @роль, которую Вы хотите купить\n```")
        await ctx.reply(embed=emb)

    @commands.command(aliases=["buy_item"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy_item(self, ctx: commands.context.Context, item: int = None):
        if item is None:
            await ctx.reply(f"""{ctx.author}, укажите то, что Вы хотите приобрести""")
        else:
            async with self.session() as session:
                async with session.begin():
                    item_from_shop = await session.execute(
                        select(ShopItem).where(
                            ShopItem.item_id == item and ShopItem.guild_id == ctx.guild.id
                        )
                    )
                    item_from_shop: ShopItem = item_from_shop.scalars().first()
                    user = await session.execute(
                        select(DBUser).where(
                            DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                        )
                    )
                    user: DBUser = user.scalars().first()
                    server = await session.execute(
                        select(ServerSettings).where(ServerSettings.guild_id == ctx.guild.id)
                    )
                    server: ServerSettings = server.scalars().first()
                    if item_from_shop is None:
                        await ctx.reply(f"""{ctx.author}, такого товара не существует!""")
                    elif item_from_shop.item_cost > user.cash:
                        await ctx.reply(f"""{ctx.author}, у Вас недостаточно средств!""")
                    else:
                        user.cash -= item_from_shop.item_cost
                        await ctx.message.add_reaction('✅')
                        if server in None:
                            await ctx.send(f"Покупка {ctx.author.mention} товар номер {item}")
                            await ctx.reply("Администрация скоро выдаст Вам товар")
                            return
                        channel = self.bot.get_channel(server.channel_id)
                        await channel.send(f"Покупка {ctx.author.mention} товар номер {item}")
                        await ctx.reply("Администрация скоро выдаст Вам товар")

    @commands.command(aliases=["buy", "buy-role"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy(self, ctx: commands.context.Context, role: discord.Role = None):
        if role is None:
            await ctx.reply(f"""{ctx.author}, укажите роль, которую Вы хотите приобрести""")
        else:
            async with self.session() as session:
                async with session.begin():
                    user = await session.execute(
                        select(DBUser).where(
                            DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                        )
                    )
                    user: DBUser = user.scalars().first()
                    shop_role = await session.execute(
                        select(ShopRole).where(
                            ShopRole.guild_id == ctx.guild.id and ShopRole.role_id == role.id
                        )
                    )
                    shop_role: ShopRole = shop_role.scalars().first()
                    if role in ctx.author.roles:
                        await ctx.reply(f"""{ctx.author}, у Вас уже есть эта роль!""")
                    elif shop_role is None:
                        await ctx.reply(f"""{ctx.author}, эта роль не в магазине!""")
                    elif shop_role.role_cost > user.cash:
                        await ctx.reply(f"""{ctx.author}, у Вас недостаточно средств для покупки этой роли!""")
                    else:
                        await ctx.author.add_roles(role)
                        user.cash -= shop_role.role_cost
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["send"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send(
            self, ctx: commands.context.Context,
            member: discord.Member = None, cash: int = None
    ) -> None:
        if member is None:
            await ctx.reply(f"""{ctx.author}, укажите пользователя, которому Вы хотите перевести коины""")
        else:
            if await self._check_cash(ctx, cash, check=True):
                async with self.session() as session:
                    async with session.begin():
                        if member.id == ctx.author.id:
                            await ctx.reply(f"""{ctx.author}, Вы не можете перевести деньги себе""")
                        else:
                            user = await session.execute(
                                select(DBUser).where(
                                    DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                                )
                            )
                            user: DBUser = user.scalars().first()
                            user += cash
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["stats"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __stats(self, ctx: commands.context.Context, member: discord.Member = None) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id if member is None else member.id
                        and
                        DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                lvl = user.users_stats.chat_lvl
                all_xp = user.users_stats.xp
                xp = await session.execute(
                    select(Level).where(
                        Level.level == lvl + 1
                    )
                )
                xp = xp.scalars().first().xp - all_xp
        await ctx.reply(
            embed=create_emb(
                title="Статистика {}".format(ctx.author if member is None else member),
                args=[
                    {
                        "name": f'Coinflips - {user.users_stats.coin_flips_count}',
                        "value": f'Wins - {user.users_stats.coin_flips_wins_count}\n '
                                 f'Loses - {user.users_stats.coin_flips_defeats_count}',
                        "inline": True
                    },
                    {
                        "name": f'Rust casinos - {user.users_stats.rust_casinos_count}',
                        "value": f'Wins - {user.users_stats.rust_casinos_wins_count}\n '
                                 f'Loses - {user.users_stats.rolls_defeats_count}',
                        "inline": True
                    },
                    {
                        "name": f'Rolls - {user.users_stats.rolls_count}',
                        "value": f'Wins - {user.users_stats.rolls_wins_count}\n '
                                 f'Loses - {user.users_stats.rolls_wins_count}',
                        "inline": True
                    },
                    {
                        "name": f'Fails - {user.users_stats.fails_count}',
                        "value": f'Wins - {user.users_stats.fails_wins_count}\n '
                                 f'Loses - {user.users_stats.fails_defeats_count}',
                        "inline": True
                    },
                    {
                        "name": f'777s - {user.users_stats.three_sevens_count}',
                        "value": f'Wins - {user.users_stats.three_sevens_wins_count}\n '
                                 f'Loses - {user.users_stats.three_sevens_defeats_count}',
                        "inline": True
                    },
                    {
                        "name": 'Побед/Поражений всего',
                        "value": f'Wins - {user.users_stats.all_wins_count}\n '
                                 f'Loses - {user.users_stats.all_defeats_count}',
                        "inline": True
                    },
                    {
                        "name": 'Выиграно всего',
                        "value": divide_the_number(
                            user.users_stats.entire_amount_of_winnings
                        ),
                        "inline": True
                    },
                    {
                        "name": 'Минут в голосовых каналах',
                        "value": f'{user.users_stats.minutes_in_voice_channels} минут',
                        "inline": True
                    },
                    {
                        "name": 'Сообщений в чате',
                        "value": f'{user.users_stats.messages_count} сообщений в чате',
                        "inline": True
                    },
                    {
                        "name": f'{lvl} левел в чате',
                        "value": f'{divide_the_number(xp)} опыта до следующего левела, '
                                 f'{divide_the_number(all_xp)} опыта всего',
                        "inline": True
                    }
                ]
            )
        )

    @commands.command(aliases=["card"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __card(self, ctx: commands.context.Context) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                level = await session.execute(
                    select(Level).where(Level.level == user.users_stats[0].chat_lvl + 1)
                )
                level: Level = level.scalars().first()
                generator = CardGenerator(str(ctx.author.avatar.url)[:-10])
                generator.add_stats(
                    name=str(ctx.author),
                    wins=user.users_stats[0].all_wins_count,
                    loses=user.users_stats[0].all_defeats_count,
                    minutes_in_voice=user.users_stats[0].minutes_in_voice_channels,
                    messages=user.users_stats[0].messages_count,
                    xp=user.users_stats[0].xp
                )
                generator.add_badges(
                    verification=user.cards[0].verification,
                    developer=user.cards[0].developer,
                    coder=user.cards[0].coder,
                    fail=user.achievements[0].dropping_zero_in_fail,
                    wins_pin=user.achievements[0].wins_achievement_level,
                    loses_pin=user.achievements[0].defeat_achievements_level,
                    coin=user.cards[0].coin,
                    minutes_pin=user.achievements[0].voice_achievements_level
                )
                generator.draw_xp_bar(
                    xp=level.xp,
                    total_xp=user.users_stats[0].xp,
                    lvl=user.users_stats[0].chat_lvl
                )
                generator.add_rang()
                image_bytes = BytesIO()
                generator.img.save(image_bytes, format="png")
                image_bytes.seek(0)

                await ctx.reply(file=discord.File(fp=image_bytes, filename="card.png"))

    @commands.command(aliases=["promo"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_active(self, ctx: commands.context.Context, promo: str = None):
        async with self.session() as session:
            async with session.begin():
                promo_code = await session.execute(
                    select(PromoCode).where(
                        PromoCode.code == promo
                    )
                )
                promo_code: PromoCode = promo_code.scalars().first()
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                if promo is None:
                    await ctx.reply(f"""{ctx.author.mention}, Вы не ввели промокод!""")
                elif not promo_code:
                    await ctx.reply(f"""{ctx.author.mention}, такого промокода не существует!""")
                elif promo_code.global_status == 0 and ctx.guild.id != promo_code.guild_id:
                    await ctx.reply(
                        f"""{ctx.author.mention}, Вы не можете использовать этот промокод на этом данном сервере!"""
                    )
                else:
                    cash = promo_code.cash
                    user.cash += cash
                    await session.execute(
                        delete(promo_code)
                    )
                    emb = discord.Embed(title="Промокод", colour=get_color(ctx.author.roles))
                    emb.add_field(
                        name=f'Промокод активирован!',
                        value=f'Вам начислено **{divide_the_number(cash)}** коинов!',
                        inline=False
                    )
                    await ctx.reply(embed=emb)

    @commands.command(aliases=['gift'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __gift(
            self, ctx: commands.context.Context,
            member: discord.Member = None, role: discord.Role = None
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                shop = await session.execute(
                    select(ShopRole).where(
                        ShopRole.role_id == role.id and ShopRole.guild_id == ctx.guild.id
                    )
                )
                shop: ShopRole = shop.scalars().first()
                if role is None:
                    await ctx.reply(f"""{ctx.author}, укажите роль, которую Вы хотите приобрести""")
                elif member is None:
                    await ctx.reply(f"""{ctx.author}, укажите человека, которому Вы хотите подарить роль""")
                else:
                    if role in member.roles:
                        await ctx.reply(f"""{ctx.author}, у Вас уже есть эта роль!""")

                    elif shop.role_cost > user.cash:
                        await ctx.reply(f"""{ctx.author}, у Вас недостаточно денег для покупки этой роли!""")
                    else:
                        await member.add_roles(role)
                        user.cash -= shop.role_cost
                        await ctx.message.add_reaction('✅')

    @commands.command(aliases=["promos"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_codes(self, ctx: commands.context.Context) -> None:
        async with self.session() as session:
            async with session.begin():
                promo_codes = await session.execute(
                    select(PromoCode).where(
                        PromoCode.user_id == ctx.author.id
                    )
                )
                promo_codes = promo_codes.scalars()
                code: PromoCode
                if ctx.guild is None:
                    if not promo_codes:
                        await ctx.author.send(f"{ctx.author.mention}, у Вас нет промокодов!")
                    else:
                        emb = discord.Embed(title="Промокоды")
                        for codes in promo_codes:
                            server = self.bot.get_guild(codes.guild_id)
                            if server is not None:
                                emb.add_field(
                                    name=f"{server} - {codes.cash}",
                                    value=f"{codes.code}",
                                    inline=False
                                )
                        await ctx.author.send(embed=emb)
                else:
                    await ctx.reply(
                        f"{ctx.author.mention}, эту команду можно использовать только в личных сообщениях бота"
                    )

    @commands.command(aliases=["promo_create"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_create(self, ctx: commands.context.Context, cash: int = None, key: str = None) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.author.id
                    )
                )
                user: DBUser = user.scalars().first()
                if cash is None:
                    await ctx.reply(f'{ctx.author.mention}, Вы не ввели сумму!')
                elif cash > user.cash:
                    await ctx.reply(f"""{ctx.author.mention}, у Вас недостаточно денег для создания промокода!""")
                elif cash < 1:
                    await ctx.reply(f"""{ctx.author.mention}, не-не-не:)""")
                elif ctx.guild is None:
                    pass
                else:
                    code = get_promo_code(10)
                    if key == "global" and ctx.author.id == 401555829620211723:
                        new_promo_code = PromoCode()
                        new_promo_code.user_id = ctx.author.id
                        new_promo_code.guild_id = ctx.guild.id
                        new_promo_code.cash = cash
                        new_promo_code.global_status = 1
                        session.add(new_promo_code)
                    else:
                        new_promo_code = PromoCode()
                        new_promo_code.user_id = ctx.author.id
                        new_promo_code.guild_id = ctx.guild.id
                        new_promo_code.cash = cash
                        new_promo_code.global_status = 0
                        session.add(new_promo_code)
                        user.cash -= cash
                    try:
                        await ctx.author.send(code)
                        emb = discord.Embed(title="Промокод", colour=get_color(ctx.author.roles))
                        emb.add_field(
                            name=f'Ваш промокод на **{divide_the_number(cash)}**',
                            value=f'Промокод отправлен Вам в личные сообщения!',
                            inline=False
                        )
                        await ctx.reply(embed=emb)
                    except discord.Forbidden:
                        code2 = code
                        code = ""
                        for i in range(len(code2)):
                            if i > len(code2) - 4:
                                code += "*"
                            else:
                                code += code2[i]
                        emb = discord.Embed(title="Промокод", colour=get_color(ctx.author.roles))
                        emb.add_field(
                            name=f'Ваш промокод на **{divide_the_number(cash)}**',
                            value=f'{divide_the_number(code)}\nЧтобы получить все Ваши промокоды, '
                                  f'Вы можете написать //promos в личные сообщения бота\n'
                                  f'Если у Вас возникнет ошибка отправки, '
                                  f'Вам необходимо включить личные сообщения от участников '
                                  f'сервера, после отправки сообщения '
                                  f'эту функцию можно выключить.',
                            inline=False
                        )
                        await ctx.reply(embed=emb)

    @commands.command(aliases=["gpt"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def __gpt(self, ctx: commands.context.Context, message: str) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                if ctx.guild is not None:
                    if user.cash < 10000:
                        await ctx.reply(f"{ctx.author.mention}, у вас недостаточно средств!")
                        return
                    if ctx.author.id not in self.gpt_users.keys():
                        self.gpt_users[ctx.author.id] = GTP3Model(self.gpt_token)
                    user.cash -= 10000
                    await ctx.reply(self.gpt_users[ctx.author.id].answer(message))
                else:
                    await ctx.reply(f"{ctx.author.mention}, эту команду нельзя использовать в личных сообщениях бота")

    @commands.command(aliases=["gpt-context"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def __gpt(self, ctx: commands.context.Context, message: str) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == ctx.author.id and DBUser.guild_id == ctx.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                if ctx.guild is not None:
                    if user.cash < 20000:
                        await ctx.reply(f"{ctx.author.mention}, у вас недостаточно средств!")
                        return
                    if ctx.author.id not in self.gpt_users.keys():
                        self.gpt_users[ctx.author.id] = GTP3Model(self.gpt_token)
                    user.cash -= 20000
                    await ctx.reply(self.gpt_users[ctx.author.id].answer_with_context(message))
                else:
                    await ctx.reply(f"{ctx.author.mention}, эту команду нельзя использовать в личных сообщениях бота")
