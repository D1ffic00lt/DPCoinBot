# -*- coding: utf-8 -*-
import logging
import discord

from typing import Callable, Union
from discord.ext import commands
from discord.utils import get
from discord import app_commands
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.guild.servers import ServerSettings
from database.user.users import User
from units.texts import need_settings
from units.additions import divide_the_number

__all__ = (
    "GuildSlash",
)


class GuildSlash(commands.Cog):
    NAME = 'guild module'

    __slots__ = (
        "db", "bot", "found", "admin",
        "casino_channel", "role", "auto",
        "category", "emb", "guild"
    )

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.bot = bot
        logging.info(f"Guild (Slash) connected")

    async def _check_for_guild_existence_in_table(self, guild_id):
        async with self.session() as session:
            async with session.begin():
                guild = await session.execute(
                    select(ServerSettings).where(ServerSettings.guild_id == guild_id)
                )
                guild = guild.scalars().first()
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
            await inter.response.send_message(message)
            return
        async with self.session() as session:
            user = await session.execute(
                select(User).where(User.user_id == inter.user.id and User.guild_id == inter.guild.id)
            )
            user: User = user.scalars().first()
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

    @app_commands.command(name="auto_setup", description="Авто-настройка сервера")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __cat_create(self, inter: discord.Interaction) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            guild = inter.message.guild
            db_guild: Union[None, ServerSettings] = self._check_for_guild_existence_in_table(inter.guild.id)
            if db_guild:
                admin_channel = self.bot.get_channel(db_guild.channel_id)
                casino_channel = self.bot.get_channel(db_guild.casino_channel_id)
                admin_role = get(guild.roles, id=db_guild.administrator_role_id)
                if casino_channel is not None:
                    await casino_channel.delete()
                if admin_channel is not None:
                    await admin_channel.delete()
                if admin_role is not None:
                    await admin_role.delete()
                if db_guild.auto_setup == 1:
                    found = False
                    bot_category = None
                    for category in guild.categories:
                        if category.id == db_guild.category_id:
                            bot_category: discord = category
                            found = True
                            break
                    if found:
                        await bot_category.delete()

            bot_category = await guild.create_category("DPCoinBot")
            casino_channel = await guild.create_text_channel(name=f'Casino', category=bot_category)
            admin_channel = await guild.create_text_channel(name=f'shop_list', category=bot_category)
            admin_role = await guild.create_role(name="Coin Manager", colour=discord.Colour.from_rgb(255, 228, 0))
            async with self.session() as session:
                async with session.begin():
                    await session.execute(
                        delete(ServerSettings).where(ServerSettings.guild_id == inter.guild.id)
                    )
                    await session.commit()
                    new_server_settings = ServerSettings()
                    new_server_settings.guild_id = inter.guild.id
                    new_server_settings.category_id = bot_category.id
                    new_server_settings.casino_channel_id = casino_channel.id
                    new_server_settings.channel_id = admin_channel.id
                    new_server_settings.administrator_role_id = admin_role.id
                    session.add(new_server_settings)

            await admin_channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
            emb = discord.Embed(title="Канал для казино")
            emb.add_field(
                name=f'Развлекайтесь!',
                value='Да будет анархия!',
                inline=False)
            await casino_channel.send(embed=emb)
            emb = discord.Embed(title="Канал для заказов")
            emb.add_field(
                name=f'Настройте его, пожалуйста🥺',
                value='Разрешите каким-то холопам просматривать этот канал, если конечно же хотите:D',
                inline=False)
            await admin_channel.send(embed=emb)
            emb = discord.Embed(title="Категория создана")
            emb.add_field(
                name=f'Требуется дополнительная настройка!',
                value=need_settings.format(casino_channel.mention, admin_channel.mention, admin_role.mention),
                inline=False)
            await inter.response.send_message(embed=emb)

    @app_commands.command(name="start_money", description="Стартовый баланс")
    @app_commands.choices(arg=[
        app_commands.Choice(name="Получить", value="get"),
        app_commands.Choice(name="Установить", value="set")
    ])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __start_money(
            self, inter: discord.Interaction, arg: app_commands.Choice[str] = None, cash: int = None
    ) -> None:
        if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
            guild: Union[None, ServerSettings] = self._check_for_guild_existence_in_table(inter.guild.id)
            if arg == "set":
                if await self._check_cash(inter, cash, max_cash=1000000) or cash == 0:
                    if not guild:
                        await inter.response.send_message(
                            f"{inter.user.mention}, сервер ещё не настроен! "
                            f"Сперва проведите настройку сервера!(auto_setup)"
                        )
                    else:
                        async with self.session() as session:
                            async with session.begin():
                                guild = await session.execute(
                                    select(ServerSettings).where(
                                        ServerSettings.guild_id == inter.guild.id
                                    )
                                )
                                guild.starting_balance = cash
                        await inter.response.send_message('✅')
            elif arg is None:
                if not self._check_for_guild_existence_in_table(inter.guild.id):
                    await inter.response.send_message(
                        f"{inter.user.mention}, сервер ещё не настроен! "
                        f"Сперва проведите настройку сервера!(auto_setup)"
                    )
                else:
                    await inter.response.send_message(
                        f"На данный момент при входе дают "
                        f"**{divide_the_number(guild.starting_balance)}** DP коинов"
                    )
