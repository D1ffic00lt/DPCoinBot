# -*- coding: utf-8 -*-
import logging
import discord

from discord.ext import commands
from discord.utils import get
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Union

from database.guild.servers import ServerSettings
from database.user.users import User
from units.texts import need_settings
from units.additions import divide_the_number

__all__ = (
    "Guild",
)


class Guild(commands.Cog):
    NAME = 'guild module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.bot = bot
        logging.info(f"Guild connected")

    async def _check_for_guild_existence_in_table(self, guild_id):
        async with self.session() as session:
            async with session.begin():
                guild = await session.execute(
                    select(ServerSettings).where(ServerSettings.guild_id == guild_id)
                )
                guild = guild.scalars().first()
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

    @commands.command(aliases=["auto_setup"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __cat_create(self, ctx: commands.context.Context) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            guild = ctx.message.guild
            db_guild: Union[None, ServerSettings] = self._check_for_guild_existence_in_table(ctx.guild.id)
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
                        delete(ServerSettings).where(ServerSettings.guild_id == ctx.guild.id)
                    )
                    await session.commit()
                    new_server_settings = ServerSettings()
                    new_server_settings.guild_id = ctx.guild.id
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
            await ctx.reply(embed=emb)

    @commands.command(aliases=["start_money"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __start_money(self, ctx: commands.context.Context, arg: str = None, cash: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            guild: Union[None, ServerSettings] = self._check_for_guild_existence_in_table(ctx.guild.id)
            if arg == "set":
                if await self._check_cash(ctx, cash, max_cash=1000000) or cash == 0:
                    if not guild:
                        await ctx.reply(
                            f"{ctx.author.mention}, сервер ещё не настроен! "
                            f"Сперва проведите настройку сервера!(auto_setup)"
                        )
                    else:
                        async with self.session() as session:
                            async with session.begin():
                                guild = await session.execute(
                                    select(ServerSettings).where(
                                        ServerSettings.guild_id == ctx.guild.id
                                    )
                                )
                                guild.starting_balance = cash
                        await ctx.message.add_reaction('✅')
            elif arg is None:
                if not self._check_for_guild_existence_in_table(ctx.guild.id):
                    await ctx.reply(
                        f"{ctx.author.mention}, сервер ещё не настроен! "
                        f"Сперва проведите настройку сервера!(auto_setup)"
                    )
                else:
                    await ctx.reply(
                        f"На данный момент при входе дают "
                        f"**{divide_the_number(guild.starting_balance)}** DP коинов"
                    )
