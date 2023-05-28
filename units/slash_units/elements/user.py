# -*- coding: utf-8 -*-
import os
import logging
from io import BytesIO

import discord

from discord.ext import commands
from discord import app_commands
from typing import Callable, Union

from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config import PREFIX
from database.bot.levels import Level
from database.guild.item_shops import ShopItem
from database.guild.promo_codes import PromoCode
from database.guild.servers import ServerSettings
from database.guild.shops import ShopRole
from database.user.stats import UserStats
from units.additions import (
    get_time, create_emb,
    divide_the_number, get_color,
    get_promo_code
)
from units.card_generator import CardGenerator
from units.json_logging import Json
from units.gpt import GPT3Model
from database.user.users import User as DBUser
__all__ = (
    "UserSlash",
)


class UserSlash(commands.Cog):
    NAME = 'user slash module'

    __slots__ = (
        "db", "bot", "name", "color", "all_cash",
        "level", "counter", "index", "ID",
        "guild_id", "server", "js",
        "emb", "img", "image_draw", "wins",
        "loses", "minutes_id_voice", "messages", "cash",
        "code", "code2", "response", "avatar"
    )

    def __init__(self, bot: commands.Bot, session, gpt_token: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.bot: commands.Bot = bot
        self.gpt_token = gpt_token
        self.bot: commands.Bot = bot
        self.gpt_users: dict[int, GPT3Model] = {}
        logging.info(f"User (slash) connected")

    async def _check_cash(
            self, inter: discord.Interaction,
            cash: Union[str, int], max_cash: int = None,
            min_cash: int = 1, check: bool = False
    ) -> bool:
        mention = inter.user.mention
        author_id = inter.user.id
        if cash is None:
            message = f"{mention}, Вы не ввели сумму!"
            await inter.response.send_message(message)
            return
        async with self.session() as session:
            user = await session.execute(
                select(DBUser).where(DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id)
            )
            user: DBUser = user.scalars().first()
            if not user:
                await inter.response.send_message("no user")
                return False
        if check and cash > user.cash:
            message = f"{mention}, у Вас недостаточно средств!"
            await inter.response.send_message(message)
        else:
            if cash == "all":
                return True
            elif max_cash is not None:
                if (int(cash) < min_cash or int(cash) > max_cash) and author_id != 401555829620211723:
                    message = f'{mention}, нельзя ввести число меньше ' \
                                   f'{divide_the_number(min_cash)} и больше {divide_the_number(max_cash)}!'
                    await inter.response.send_message(message)
                else:
                    return True
            elif max_cash is None:
                if int(cash) < min_cash and inter.user.id != 401555829620211723:
                    message = f'{mention}, нельзя ввести число меньше {divide_the_number(min_cash)}!'
                    await inter.response.send_message(message)
                else:
                    return True
        return False

    @app_commands.command(name="update", description="Информация об обновлении")
    async def __update(self, inter: discord.Interaction):
        await inter.response.send_message("123")

    @app_commands.command(name="cash", description="Узнать свой баланс")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __balance(
            self, inter: discord.Interaction,
            member: discord.Member = None
    ) -> None:
        if member is None:
            try:
                async with self.session() as session:
                    async with session.begin():
                        user = await session.execute(
                            select(DBUser).where(
                                DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                            )
                        )
                        user = user.scalars().first()
                        await inter.response.send_message(
                            embed=create_emb(
                                title="Баланс",
                                description=f"Баланс пользователя ```{inter.user}``` составляет "
                                            f"```{divide_the_number(user.cash)}``` "
                                            f"DP коинов"
                            )
                        )
            except TypeError:
                logging.error(f"TypeError: user.py (slash) 79 cash")
        else:
            async with self.session() as session:
                async with session.begin():
                    user = await session.execute(
                        select(DBUser).where(
                            DBUser.user_id == member.id and DBUser.guild_id == inter.guild.id
                        )
                    )
                    user = user.scalars().first()
                    await inter.response.send_message(
                        embed=create_emb(
                            title="Баланс",
                            description=f"Баланс пользователя ```{member}``` составляет "
                                        f"```{divide_the_number(user.cash)}``` DP коинов"
                        )
                    )

    @app_commands.command(name="bank", description="Узнать баланс в банке (в разработке)")
    @app_commands.choices(action=[
        app_commands.Choice(name="Положить", value="add"),
        app_commands.Choice(name="Снять", value="take")
    ])
    async def __bank(
            self, inter: discord.Interaction,
            action: app_commands.Choice[str] = None,
            cash: int = None
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                if action is None:
                    all_cash = user.cash + user.cash_in_bank
                    await inter.response.send_message(
                        embed=create_emb(
                            title="Баланс",
                            description=f"Баланс пользователя ```{inter.user}``` составляет "
                                        f"```{divide_the_number(user.cash)}```"
                                        f" DP коинов\n\nБаланс в банке составляет"
                                        f"```{divide_the_number(user.cash_in_bank)}``` "
                                        f"DP коинов\n\nВсего коинов - `"
                                        f"{divide_the_number(all_cash)}"
                        )
                    )
                elif action.value == "add":
                    if await self._check_cash(inter, cash):
                        user.cash_in_bank += cash
                        await inter.response.send_message('✅')

                elif action.value == "take":
                    if cash == "all":
                        user.cash += user.cash_in_bank
                        user.cash_in_bank = 0
                    else:
                        if cash is None:
                            await inter.response.send_message(f"""{inter.user.mention}, Вы не ввели сумму!""")
                        elif cash > user.cash_in_bank:
                            await inter.response.send_message(f"""{inter.user.mention}, у Вас недостаточно средств!""")
                        if await self._check_cash(inter, cash):
                            user.cash += cash
                            user.cash_in_bank -= cash
                            await inter.response.send_message('✅')

    @app_commands.command(name="slb", description="Общий баланс сервера")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __slb(self, inter: discord.Interaction) -> None:
        all_cash = 0
        color = get_color(inter.user.roles)
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            js = {"lb": True, "slb": True}
        else:
            js = Json(".json/develop_get.json").json_load()
        async with self.session() as session:
            async with session.begin():
                users = await session.execute(
                    select(DBUser).where(DBUser.user_id == inter.guild.id).order_by(DBUser.cash)
                )
                users = users.scalars()

                for user in users:
                    name = self.bot.get_user(user.user_id)
                    if name is not None and not name.bot:
                        for member in inter.guild.members:
                            if name.id == member.id:
                                if name.id == 401555829620211723 and \
                                        inter.guild.id == 493970394374471680 and js["slb"] is False:
                                    pass
                                else:
                                    all_cash += user.cash
                                break
        await inter.response.send_message(
            embed=create_emb(
                title="Общий баланс сервера:",
                color=color,
                args=[
                    {
                        "name": f"Баланс сервера {inter.guild}",
                        "value": f"Общий баланс сервера {inter.guild} составляет "
                                 f"{divide_the_number(all_cash)} "
                                 f" DP коинов",
                        "inline": False
                    }
                ]
            )
        )

    @app_commands.command(name="lb", description="Лидерборд сервера")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Чат", value="chat"),
        app_commands.Choice(name="Войс", value="voice"),
        app_commands.Choice(name="Репутация", value="rep")
    ])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __lb(self, inter: discord.Interaction, mode: app_commands.Choice[str] = None) -> None:
        counter = 0
        index = 0
        if not os.path.exists(".json/develop_get.json"):
            Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
            js = {"lb": True, "slb": True}
        else:
            js = Json(".json/develop_get.json").json_load()
        if mode.value is None:
            emb = discord.Embed(title="Топ 10 сервера")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == inter.guild.id
                        ).order_by(desc(DBUser.cash))
                    )
                    users = users.scalars().all()
                    for user in users:
                        user: DBUser = user
                        if index == 10:
                            break
                        name = self.bot.get_user(user.user_id)

                        if not name.bot:
                            if name.id == 401555829620211723 and inter.guild.id == 493970394374471680 \
                                    and js["lb"] is False:
                                continue
                            else:
                                counter += 1
                                emb.add_field(
                                    name=f'# {counter} | `{name.name}` | lvl `{user.users_stats[0].chat_lvl}`',
                                    value=f'Баланс: {divide_the_number(user.cash)}',
                                    inline=False
                                )
                                index += 1

                    await inter.response.send_message(embed=emb)
        elif mode.value == "chat":
            emb = discord.Embed(title="Топ 10 сервера по левелу")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == inter.guild.id
                        ).join(UserStats, DBUser.users_stats).order_by(desc(UserStats.xp))
                    )
                    users = users.scalars()
                    for user in users:
                        if index == 10:
                            break
                        name = self.bot.get_user(user.user_id)

                        if not name.bot:
                            counter += 1
                            emb.add_field(
                                name=f'# {counter} | `{name.name}` | chat lvl `{user.users_stats[0].chat_lvl}`',
                                value=f'xp: **{divide_the_number(user.users_stats[0].xp)}**',
                                inline=False
                            )
                            index += 1

                    await inter.response.send_message(embed=emb)
        elif mode.value == "voice":
            emb = discord.Embed(title="Топ 10 сервера по времени в голосовых каналах")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == inter.guild.id).join(
                            UserStats, DBUser.users_stats
                        ).order_by(
                            desc(UserStats.minutes_in_voice_channels)
                        )
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
                                value=f'**{divide_the_number(user.users_stats[0].minutes_in_voice_channels)} минут '
                                      f'({divide_the_number(user.users_stats[0].minutes_in_voice_channels / 60)} '
                                      f'часов)**',
                                inline=False
                            )
                            index += 1

                    await inter.response.send_message(embed=emb)
        elif mode.value == "rep":
            emb = discord.Embed(title="Топ 10 сервера")
            async with self.session() as session:
                async with session.begin():
                    users = await session.execute(
                        select(DBUser).where(
                            DBUser.guild_id == inter.guild.id).order_by(
                            DBUser.users_stats[0].reputation
                        ).limit(10)
                    )
                    users = users.scalars()
                    counter = 0
                    for user in users:
                        counter += 1
                        emb.add_field(
                            name=f'# {counter} | `{self.bot.get_user(user.user_id).name}`',
                            value=f'Репутация: {user.users_stats[0].reputation}',
                            inline=False
                        )
                    await inter.response.send_message(embed=emb)

    @app_commands.command(name="shop", description="Магазин ролей")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __shop(self, inter: discord.Interaction):
        emb = discord.Embed(title="Магазин ролей")
        async with self.session() as session:
            async with session.begin():
                shops = await session.execute(
                    select(ShopRole).where(ShopRole.guild_id == inter.guild.id).order_by(ShopRole.role_cost)
                )
                shops = shops.scalars()
                item_shops = await session.execute(
                    select(ShopItem).where(ShopItem.guild_id == inter.guild.id).order_by(ShopItem.item_cost)
                )
                item_shops = item_shops.scalars()
                for role in shops:
                    if inter.guild.get_role(role.role_id) is not None:
                        emb.add_field(
                            name=f'Роль {inter.guild.get_role(role.role_id).mention}',
                            value=f'Стоимость: **{role.role_cost} DP коинов**',
                            inline=False
                        )
                emb.add_field(name="**Как купить роль?**",
                              value=f'''```diff\n- {PREFIX}buy <Упоминание роли>\n```''')
                if item_shops.first() is not None:
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
                await inter.response.send_message(embed=emb)

    @app_commands.command(name="buy_item", description="Купить товар из магазина")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy_item(self, inter: discord.Interaction, item: int):
        if item is None:
            await inter.response.send_message(f"""{inter.user}, укажите то, что Вы хотите приобрести""")
        else:
            async with self.session() as session:
                async with session.begin():
                    item_from_shop = await session.execute(
                        select(ShopItem).where(
                            ShopItem.item_id == item and ShopItem.guild_id == inter.guild.id
                        )
                    )
                    item_from_shop: ShopItem = item_from_shop.scalars().first()
                    user = await session.execute(
                        select(DBUser).where(
                            DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                        )
                    )
                    user: DBUser = user.scalars().first()
                    server = await session.execute(
                        select(ServerSettings).where(ServerSettings.guild_id == inter.guild.id)
                    )
                    server: ServerSettings = server.scalars().first()
                    if item_from_shop is None:
                        await inter.response.send_message(f"""{inter.user}, такого товара не существует!""")
                    elif item_from_shop.item_cost > user.cash:
                        await inter.response.send_message(f"""{inter.user}, у Вас недостаточно средств!""")
                    else:
                        user.cash -= item_from_shop.item_cost
                        await inter.response.send_message('✅')
                        if server in None:
                            await inter.channel.send(f"Покупка {inter.user.mention} товар номер {item}")
                            await inter.response.send_message("Администрация скоро выдаст Вам товар")
                            return
                        channel = self.bot.get_channel(server.channel_id)
                        await channel.send(f"Покупка {inter.user.mention} товар номер {item}")
                        await inter.response.send_message("Администрация скоро выдаст Вам товар")

    @app_commands.command(name="buy", description="Купить роль из магазина")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __buy(self, inter: discord.Interaction, role: discord.Role):
        if role is None:
            await inter.response.send_message(f"""{inter.user}, укажите роль, которую Вы хотите приобрести""")
        else:
            async with self.session() as session:
                async with session.begin():
                    user = await session.execute(
                        select(DBUser).where(
                            DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                        )
                    )
                    user: DBUser = user.scalars().first()
                    shop_role = await session.execute(
                        select(ShopRole).where(
                            ShopRole.guild_id == inter.guild.id and ShopRole.role_id == role.id
                        )
                    )
                    shop_role: ShopRole = shop_role.scalars().first()
                    if role in inter.user.roles:
                        await inter.response.send_message(f"""{inter.user}, у Вас уже есть эта роль!""")
                    elif shop_role is None:
                        await inter.response.send_message(f"""{inter.user}, эта роль не в магазине!""")
                    elif shop_role.role_cost > user.cash:
                        await inter.response.send_message(
                            f"""{inter.user}, у Вас недостаточно средств для покупки этой роли!"""
                        )
                    else:
                        await inter.user.add_roles(role)
                        user.cash -= shop_role.role_cost
                        await inter.response.send_message('✅')

    @app_commands.command(name="send", description="Перевести коины другому пользователю")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __send(
            self, inter: discord.Interaction,
            member: discord.Member, cash: int
    ) -> None:
        if member is None:
            await inter.response.send_message(
                f"""{inter.user}, укажите пользователя, которому Вы хотите перевести коины"""
            )
        else:
            if await self._check_cash(inter, cash, check=True):
                async with self.session() as session:
                    async with session.begin():
                        if member.id == inter.user.id:
                            await inter.response.send_message(f"""{inter.user}, Вы не можете перевести деньги себе""")
                        else:
                            user = await session.execute(
                                select(DBUser).where(
                                    DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                                )
                            )
                            user: DBUser = user.scalars().first()
                            user += cash
                        await inter.response.send_message('✅')

    @app_commands.command(name="stats", description="Статистика")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __stats(self, inter: discord.Interaction, member: discord.Member = None) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == inter.user.id
                        if member is None else member.id and DBUser.guild_id == inter.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                lvl = user.users_stats[0].chat_lvl
                all_xp = user.users_stats[0].xp
                xp = await session.execute(
                    select(Level).where(
                        Level.level == lvl + 1
                    )
                )
                xp = xp.scalars().first().xp - all_xp
                await inter.response.send_message(
                    embed=create_emb(
                        title="Статистика {}".format(inter.user if member is None else member),
                        args=[
                            {
                                "name": f'Coinflips - {user.users_stats[0].coin_flips_count}',
                                "value": f'Wins - {user.users_stats[0].coin_flips_wins_count}\n '
                                         f'Loses - {user.users_stats[0].coin_flips_defeats_count}',
                                "inline": True
                            },
                            {
                                "name": f'Rust casinos - {user.users_stats[0].rust_casinos_count}',
                                "value": f'Wins - {user.users_stats[0].rust_casinos_wins_count}\n '
                                         f'Loses - {user.users_stats[0].rolls_defeats_count}',
                                "inline": True
                            },
                            {
                                "name": f'Rolls - {user.users_stats[0].rolls_count}',
                                "value": f'Wins - {user.users_stats[0].rolls_wins_count}\n '
                                         f'Loses - {user.users_stats[0].rolls_wins_count}',
                                "inline": True
                            },
                            {
                                "name": f'Fails - {user.users_stats[0].fails_count}',
                                "value": f'Wins - {user.users_stats[0].fails_wins_count}\n '
                                         f'Loses - {user.users_stats[0].fails_defeats_count}',
                                "inline": True
                            },
                            {
                                "name": f'777s - {user.users_stats[0].three_sevens_count}',
                                "value": f'Wins - {user.users_stats[0].three_sevens_wins_count}\n '
                                         f'Loses - {user.users_stats[0].three_sevens_defeats_count}',
                                "inline": True
                            },
                            {
                                "name": 'Побед/Поражений всего',
                                "value": f'Wins - {user.users_stats[0].all_wins_count}\n '
                                         f'Loses - {user.users_stats[0].all_defeats_count}',
                                "inline": True
                            },
                            {
                                "name": 'Выиграно всего',
                                "value": divide_the_number(
                                    user.users_stats[0].entire_amount_of_winnings
                                ),
                                "inline": True
                            },
                            {
                                "name": 'Минут в голосовых каналах',
                                "value": f'{user.users_stats[0].minutes_in_voice_channels} минут',
                                "inline": True
                            },
                            {
                                "name": 'Сообщений в чате',
                                "value": f'{user.users_stats[0].messages_count} сообщений в чате',
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

    @app_commands.command(name="card", description="Карточка сервера (в разработке)")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __card(self, inter: discord.Interaction) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                level = await session.execute(
                    select(Level).where(Level.level == user.users_stats[0].chat_lvl + 1)
                )
                level: Level = level.scalars().first()
                generator = CardGenerator(str(inter.user.avatar.url)[:-10])
                generator.add_stats(
                    name=str(inter.user),
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

                await inter.response.send_message(file=discord.File(fp=image_bytes, filename="card.png"))

    @app_commands.command(name="promo", description="Активировать промокод")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_active(self, inter: discord.Interaction, promo: str):
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
                        DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                if promo is None:
                    await inter.response.send_message(f"""{inter.user.mention}, Вы не ввели промокод!""")
                elif not promo_code:
                    await inter.response.send_message(f"""{inter.user.mention}, такого промокода не существует!""")
                elif promo_code.global_status == 0 and inter.guild.id != promo_code.guild_id:
                    await inter.response.send_message(
                        f"""{inter.user.mention}, Вы не можете использовать этот промокод на этом данном сервере!"""
                    )
                else:
                    cash = promo_code.cash
                    user.cash += cash
                    await session.execute(
                        delete(PromoCode).where(PromoCode.code == promo_code.code)
                    )
                    emb = discord.Embed(title="Промокод", colour=get_color(inter.user.roles))
                    emb.add_field(
                        name=f'Промокод активирован!',
                        value=f'Вам начислено **{divide_the_number(cash)}** коинов!',
                        inline=False
                    )
                    await inter.response.send_message(embed=emb)

    @app_commands.command(name="gift", description="Подарить роль из магазина")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __gift(
            self, inter: discord.Interaction,
            member: discord.Member, role: discord.Role
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == inter.user.id and DBUser.guild_id == inter.guild.id
                    )
                )
                user: DBUser = user.scalars().first()
                shop = await session.execute(
                    select(ShopRole).where(
                        ShopRole.role_id == role.id and ShopRole.guild_id == inter.guild.id
                    )
                )
                shop: ShopRole = shop.scalars().first()
                if role is None:
                    await inter.response.send_message(f"""{inter.user}, укажите роль, которую Вы хотите приобрести""")
                elif member is None:
                    await inter.response.send_message(
                        f"""{inter.user}, укажите человека, которому Вы хотите подарить роль"""
                    )
                else:
                    if role in member.roles:
                        await inter.response.send_message(f"""{inter.user}, у Вас уже есть эта роль!""")

                    elif shop.role_cost > user.cash:
                        await inter.response.send_message(
                            f"""{inter.user}, у Вас недостаточно денег для покупки этой роли!"""
                        )
                    else:
                        await member.add_roles(role)
                        user.cash -= shop.role_cost
                        await inter.response.send_message('✅')

    @app_commands.command(name="promos", description="Все ваши промокоды")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_codes(self, inter: discord.Interaction) -> None:
        async with self.session() as session:
            async with session.begin():
                promo_codes = await session.execute(
                    select(PromoCode).where(
                        PromoCode.user_id == inter.user.id
                    )
                )
                promo_codes = promo_codes.scalars()
                code: PromoCode
                if inter.guild is None:
                    if not promo_codes:
                        await inter.user.send(f"{inter.user.mention}, у Вас нет промокодов!")
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
                        await inter.user.send(embed=emb)
                else:
                    await inter.response.send_message(
                        f"{inter.user.mention}, эту команду можно использовать только в личных сообщениях бота"
                    )

    @app_commands.command(name="promo_create", description="Создать промокод")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_create(self, inter: discord.Interaction, cash: int, key: str = None) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(DBUser).where(
                        DBUser.user_id == inter.user.id and DBUser.guild_id == inter.user.id
                    )
                )
                user: DBUser = user.scalars().first()
                if cash is None:
                    await inter.response.send_message(f'{inter.user.mention}, Вы не ввели сумму!')
                elif cash > user.cash:
                    await inter.response.send_message(
                        f"""{inter.user.mention}, у Вас недостаточно денег для создания промокода!"""
                    )
                elif cash < 1:
                    await inter.response.send_message(f"""{inter.user.mention}, не-не-не:)""")
                elif inter.guild is None:
                    pass
                else:
                    code = get_promo_code(10)
                    if key == "global" and inter.user.id == 401555829620211723:
                        new_promo_code = PromoCode()
                        new_promo_code.user_id = inter.user.id
                        new_promo_code.guild_id = inter.guild.id
                        new_promo_code.cash = cash
                        new_promo_code.code = code
                        new_promo_code.global_status = 1
                        session.add(new_promo_code)
                    else:
                        new_promo_code = PromoCode()
                        new_promo_code.user_id = inter.user.id
                        new_promo_code.guild_id = inter.guild.id
                        new_promo_code.cash = cash
                        new_promo_code.code = code
                        new_promo_code.global_status = 0
                        session.add(new_promo_code)
                        user.cash -= cash
                    try:
                        await inter.user.send(code)
                        emb = discord.Embed(title="Промокод", colour=get_color(inter.user.roles))
                        emb.add_field(
                            name=f'Ваш промокод на **{divide_the_number(cash)}**',
                            value=f'Промокод отправлен Вам в личные сообщения!',
                            inline=False
                        )
                        await inter.response.send_message(embed=emb)
                    except discord.Forbidden:
                        code2 = code
                        code = ""
                        for i in range(len(code2)):
                            if i > len(code2) - 4:
                                code += "*"
                            else:
                                code += code2[i]
                        emb = discord.Embed(title="Промокод", colour=get_color(inter.user.roles))
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
                        await inter.response.send_message(embed=emb)

    @app_commands.command(name="bug_report", description="Сообщить о баге бота")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __promo_create(self, inter: discord.Interaction, command: str, description: str) -> None:
        await self.bot.get_user(401555829620211723).send(
            f"Баг репорт от {inter.user} ({inter.user.id})\n"
            f"сервер {inter.guild} ({inter.guild.id})\n"
            f"Дата {get_time()}\n"
            f"команда: {command}\n"
            f"Описание: {description}"
        )
        await inter.response.send_message("Баг репорт записан")

    @app_commands.command(name="gpt", description="Написать запрос к gpt")
    @app_commands.choices(
        model=[
            app_commands.Choice(name="GPT-3", value="gpt3"),
            app_commands.Choice(name="GPT-4 (soon)", value="gpt4")
        ],
        context=[
            app_commands.Choice(name="Да", value="yes"),
            app_commands.Choice(name="Нет", value="not")
        ]
    )
    async def __gpt(
            self, inter: discord.Interaction,
            message: str,
            model: app_commands.Choice[str] = "gpt3",
            context: app_commands.Choice[str] = "not"
    ) -> None:
        if model == "gpt3":
            model = app_commands.Choice(name="GPT-3", value="gpt3")
        if context == "not":
            context = app_commands.Choice(name="Нет", value="not")
        if inter.guild is None:
            await inter.response.send_message("no guild")
            return
        match model.value:
            case "gpt3":
                match context.value:
                    case "yes":
                        await inter.response.send_message("Please, wait...")
                        if inter.user.id not in self.gpt_users.keys():
                            self.gpt_users[inter.user.id] = GPT3Model(self.gpt_token)
                        await inter.edit_original_response(
                            content=f"```\n{await self.gpt_users[inter.user.id].answer_with_context(message)}\n```"
                        )
                    case "not":
                        if inter.user.id not in self.gpt_users.keys():
                            self.gpt_users[inter.user.id] = GPT3Model(self.gpt_token)
                        await inter.response.send_message("Please, wait...")
                        await inter.edit_original_response(
                            content=f"```\n{await self.gpt_users[inter.user.id].answer(message)}\n```"
                        )
            case "gpt4":
                await inter.response.send_message("soon...")
