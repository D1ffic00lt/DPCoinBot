# -*- coding: utf-8 -*-
import logging
import random
import discord

from typing import List, Dict, Callable, Union
from discord.ext import commands
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.bot.coinflips import CoinFlip
from database.guild.servers import ServerSettings
from database.user.achievements import Achievement
from database.user.stats import UserStats
from database.user.users import User
from units.additions import (
    fail_rand, get_color, divide_the_number,
    casino2ch, get_time, choice, total_minutes
)
from units.texts import *
from config import PREFIX

__all__ = (
    "Casino",
)


class Casino(commands.Cog):
    NAME = 'Casino module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.bot: commands.Bot = bot
        self.casino: Dict[int, Dict[str, list]] = {}
        self.rust_casino: List[int] = casino_rust.copy()
        self.texts: dict = {}
        logging.info(f"Casino connected")

    async def _is_the_casino_allowed(self, channel_id: int) -> bool:
        async with self.session() as session:
            server_settings = await session.execute(
                select(ServerSettings).where(ServerSettings.casino_channel_id == channel_id)
            )
            server_settings = server_settings.scalars().first()
            if not server_settings:
                return True
            if channel_id in [572705890524725248, 573712070864797706]:
                return True
            if server_settings.casino_channel_id == channel_id:
                return True
            return False

    async def _get_cash(self, user_id: int, guild_id: int) -> int:
        async with self.session() as session:
            user = await session.execute(
                select(User).where(User.user_id == user_id and User.guild_id == guild_id)
            )
            user = user.scalars().first()
            if not user:
                return 0
            return user.cash

    async def _take_coins(self, user_id: int, guild_id: int, count: int) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(User.user_id == user_id and User.guild_id == guild_id)
                )
                user = user.scalars().first()
                if not user:
                    return
                user.cash -= count

    async def _add_coins(self, user_id: int, guild_id: int, count: int) -> None:
        async with self.session() as session:
            user = await session.execute(
                select(User).where(User.user_id == user_id and User.guild_id == guild_id)
            )
            user = user.scalars().first()
            if not user:
                return
            user.cash += count
            await session.commit()

    async def _add_lose(self, user_id: int, guild_id: int) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(User.user_id == user_id and User.guild_id == guild_id)
                )
                user: User = user.scalars().first()
                user.achievements[0].losses += 1
                user.achievements[0].wins = 0

    async def _add_win(self, user_id: int, guild_id: int) -> None:
        async with self.session() as session:
            async with session.begin():
                user = await session.execute(
                    select(User).where(User.user_id == user_id and User.guild_id == guild_id)
                )
                user: User = user.scalars().first()
                user.achievements[0].losses = 0
                user.achievements[0].wins += 1

    async def _achievement(self, user_id: int, guild_id: int) -> None:
        guild = self.bot.get_guild(guild_id)
        user = self.bot.get_user(user_id)
        async with self.session() as session:
            async with session.begin():
                guild_user = await session.execute(
                    select(User).where(
                        User.user_id == user_id and User.guild_id == guild_id
                    )
                )
                guild_user: Union[User, None] = guild_user.scalars().first()
                if not guild_user:
                    return
                user_achievements: Achievement = guild_user.achievements[0]
                losses = user_achievements.losses
                wins = user_achievements.wins
                if user_achievements.defeat_achievements_level < 1 and losses >= 3:
                    guild_user.cash += 400
                    user_achievements.defeat_achievements_level = 1
                    await user.send(
                        f"На сервере {guild.name} "
                        f"получено достижение «Азартный человек»!\nВам начислено 400 коинов!"
                    )

                if user_achievements.defeat_achievements_level < 2 and losses >= 10:
                    guild_user.cash += 3000
                    user_achievements.defeat_achievements_level = 2
                    await user.send(
                        f"На сервере {guild.name} "
                        f"получено достижение «Сумасшедший»!\nВам начислено 3000 коинов!"
                    )
                if user_achievements.defeat_achievements_level < 3 and losses >= 20:
                    guild_user.cash += 10000
                    user_achievements.defeat_achievements_level = 3
                    await user.send(
                        f"На сервере {guild.name} "
                        f"получено достижение «Бессмертный»!\nВам начислено 10000 коинов!"
                    )

                if user_achievements.wins_achievement_level < 1 and wins >= 3:
                    guild_user.cash += 600
                    user_achievements.wins_achievement_level = 1
                    await user.send(
                        f"На сервере {guild.name} "
                        f"получено достижение «Да я богач!»!\nВам начислено 400 коинов!"
                    )
                if user_achievements.wins_achievement_level < 2 and wins >= 10:
                    guild_user.cash += 3000
                    user_achievements.wins_achievement_level = 2
                    await user.send(
                        f"На сервере {guild.name} "
                        f"получено достижение «Это вообще законно?»!\nВам начислено 3000 коинов!"
                    )

                if user_achievements.wins_achievement_level < 3 and wins >= 20:
                    guild_user.cash += 20000
                    user_achievements.wins_achievement_level = 3
                    await user.send(
                        f"На сервере {guild.name} "
                        f"получено достижение «Кажется меня не любят...»!\nВам начислено 20000 коинов!"
                    )

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

    @commands.command(aliases=['rust_casino'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_3(
            self, ctx: commands.context.Context,
            bid: int = None, number: int = None
    ) -> None:

        if self._is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.reply("Вы ну ввели Вашу ставку!")
            elif bid <= 0:
                await ctx.reply("Вы не можете поставить ставку, которая меньше 1!")
            elif self._get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.reply("У Вас не достаточно денег для этой ставки!")
            else:
                if number is None:
                    await ctx.reply("Вы не ввели число! (Либо 1, либо 3, либо 5, либо 10, либо 20)")
                else:
                    color = get_color(ctx.author.roles)
                    random.shuffle(self.rust_casino)
                    # logging.info(self.rust_casino)
                    if number in [1, 3, 5, 10, 20]:
                        await self._take_coins(ctx.author.id, ctx.guild.id, bid)

                        if self.rust_casino[0] == number:
                            await self._add_coins(ctx.author.id, ctx.guild.id, (self.rust_casino[0] * bid))
                            emb = discord.Embed(
                                title="🎰Вы выиграли!🎰",
                                colour=color
                            )
                            emb.add_field(
                                name=f'Поздравляем!',
                                value=f'{ctx.author.mention}, '
                                      f'Вы выиграли **{divide_the_number(self.rust_casino[0] * bid)}** '
                                      f'DP коинов!',
                                inline=False
                            )
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)

                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return

                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rust_casinos_count += 1
                                    user_stats.rust_casino_wins_count += 1
                                    user_stats.entire_amount_of_winnings += (self.rust_casino[0] * bid) - bid
                                    user_stats.all_wins_count += 1

                        elif self.rust_casino[0] != number:
                            emb = discord.Embed(
                                title="🎰Вы проиграли!🎰",
                                colour=color
                            )
                            emb.add_field(
                                name=f'Вы проиграли:(',
                                value=f'{ctx.author.mention}, выпало число {self.rust_casino[0]}',
                                inline=False
                            )
                            await self._add_lose(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return

                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rust_casinos_count += 1
                                    user_stats.rust_casino_loses_count += 1
                                    user_stats.entire_amount_of_winnings -= bid
                                    user_stats.all_loses_count += 1
                    else:
                        await ctx.reply(
                            f"{ctx.author.mention}, Вы должны поставить либо 1, либо 3, либо 5, либо 10, либо 20!"
                        )
        else:
            await ctx.reply(
                f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!"
                       )

    @commands.command(aliases=['fail'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __fail(
            self, ctx: commands.context.Context,
            bid: int = None, coefficient: float = None
    ) -> None:
        if self._is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.reply(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            elif coefficient is None:
                await ctx.reply(f"{ctx.author.mention}, Вы не ввели коэффициент")
            elif coefficient < 0.07:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить на коэффициент ниже 0.07")
            elif coefficient > 10:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить на коэффициент больше 10")
            elif self._get_cash(ctx.author.id, ctx.guild.id) < bid:
                await ctx.reply(f"{ctx.author.mention}, У Вас недостаточно средств")
            else:
                await self._take_coins(ctx.author.id, ctx.guild.id, bid)
                dropped_coefficient = fail_rand(ctx.author.id)[0]
                color = get_color(ctx.author.roles)
                if dropped_coefficient < coefficient:
                    emb = discord.Embed(
                        title="🎰Вы проиграли!🎰" +
                              [" Вам выпал 0.00...🎰" if dropped_coefficient == 0 else ""][0],
                        colour=color
                    )
                    emb.add_field(
                        name=f':(',
                        value=f'Выпало число `{dropped_coefficient}`\n{ctx.author}',
                        inline=False
                    )
                    await self._add_lose(ctx.author.id, ctx.guild.id)
                    await ctx.reply(embed=emb)
                    if dropped_coefficient == 0:
                        async with self.session() as session:
                            user = await session.execute(
                                select(User).where(User.id == ctx.author.id and User.guild_id == ctx.guild.id)
                            )
                            user = user.scalars().first()
                            if not user:
                                return

                        if not user.achievements[0].dropping_zero_in_fail:
                            await self._add_coins(ctx.author.id, ctx.guild.id, 4000)
                            async with self.session() as session:
                                async with session.begin():
                                    user.achievements[0].dropping_zero_in_fail = 1
                            try:
                                await ctx.author.reply(
                                    "Поздравляем, Вы забрали сумму которую поставили. А, нет, не забрали, "
                                    "разработчик до сих пор не пофиксил это...\nНу или пофиксил..."
                                    "\nВот тебе скромная награда! (4000 коинов)"
                                )
                            except discord.errors.Forbidden:
                                pass
                    async with self.session() as session:
                        async with session.begin():
                            user = await session.execute(
                                select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                            )
                            user = user.scalars().first()
                            if not user:
                                return

                            user_stats: UserStats = user.users_stats[0]
                            user_stats.fails_count += 1
                            user_stats.fails_loses_count += 1
                            user_stats.entire_amount_of_winnings -= bid
                            user_stats.all_loses_count += 1
                else:
                    await self._add_coins(ctx.author.id, ctx.guild.id, bid + int(bid * coefficient))
                    emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                    emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value=f'Выпало число `{dropped_coefficient}`\n{ctx.author}, Вы выиграли '
                              f'**{divide_the_number(bid + int(bid * coefficient))}** DP коинов!',
                        inline=False
                    )
                    await self._add_win(ctx.author.id, ctx.guild.id)
                    await ctx.reply(embed=emb)
                    async with self.session() as session:
                        async with session.begin():
                            user = await session.execute(
                                select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                            )
                            user = user.scalars().first()
                            if not user:
                                return

                            user_stats: UserStats = user.users_stats[0]
                            user_stats.fails_count += 1
                            user_stats.fails_wins_count += 1
                            user_stats.entire_amount_of_winnings += int(bid * coefficient)
                            user_stats.all_wins_count += 1
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")
        await self._achievement(ctx.author.id, ctx.guild.id)

    @commands.command(aliases=['777'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino777(self, ctx: commands.context.Context, bid: int = None) -> None:
        if self._is_the_casino_allowed(ctx.message.channel.id):
            if bid is None:
                await ctx.reply(f"{ctx.author.mention}, Вы не ввели вашу ставку")
            elif bid < 10:
                await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
            else:
                color = get_color(ctx.author.roles)
                result_bid = bid
                await self._take_coins(ctx.author.id, ctx.guild.id, bid)
                line1 = choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=7,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                line2 = choice(
                    "7", "0", "8", "1",
                    output=3, shuffle_long=9,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                line3 = choice(
                    "7", "0", "8", "1",
                    output=3,
                    shuffle_long=8,
                    array_long=5,
                    key=str(ctx.author.id)
                )
                if line2[1] == "8":
                    result_bid *= 2
                elif line2[1] == "0":
                    result_bid *= 3
                elif line2[1] == "7":
                    result_bid *= 5
                elif line2[1] == "1":
                    result_bid *= 1
                if line2[0] == line2[1] and line2[1] == line2[2]:
                    await self._add_coins(ctx.author.id, ctx.guild.id, result_bid)
                    emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                    emb.add_field(
                        name=f'🎰Поздравляем!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *line1[0], *line1[1], *line1[2],
                            *line2[0], *line2[1], *line2[2],
                            *line3[0], *line3[1], *line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await self._add_win(ctx.author.id, ctx.guild.id)
                    await ctx.reply(embed=emb)
                    async with self.session() as session:
                        async with session.begin():
                            user = await session.execute(
                                select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                            )
                            user = user.scalars().first()
                            if not user:
                                return

                            user_stats: UserStats = user.users_stats[0]
                            user_stats.three_sevens_count += 1
                            user_stats.three_sevens_wins_count += 1
                            user_stats.entire_amount_of_winnings = result_bid - bid
                            user_stats.all_wins_count += 1

                elif line1[2] == line2[1] and line2[1] == line3[0]:
                    emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                    emb.add_field(
                        name=f'🎰Вы выиграли!🎰',
                        value='`{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *line1[0], *line1[1], *line1[2],
                            *line2[0], *line2[1], *line2[2],
                            *line3[0], *line3[1], *line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await self._add_win(ctx.author.id, ctx.guild.id)
                    await self._add_coins(ctx.author.id, ctx.guild.id, result_bid)
                    await ctx.reply(embed=emb)
                    async with self.session() as session:
                        async with session.begin():
                            user = await session.execute(
                                select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                            )
                            user = user.scalars().first()
                            if not user:
                                return

                            user_stats: UserStats = user.users_stats[0]
                            user_stats.three_sevens_count += 1
                            user_stats.three_sevens_wins_count += 1
                            user_stats.entire_amount_of_winnings = result_bid - bid
                            user_stats.all_wins_count += 1

                else:
                    emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=color)
                    emb.add_field(
                        name=f':(',
                        value='{}\t{}\t{}`\n`{}\t{}\t{}`\n`{}\t{}\t{}\n{}, Вы выиграли **{}** DP коинов!'.format(
                            *line1[0], *line1[1], *line1[2],
                            *line2[0], *line2[1], *line2[2],
                            *line3[0], *line3[1], *line3[2],
                            ctx.author.mention, divide_the_number(bid),
                            inline=False
                        )
                    )
                    await self._add_lose(ctx.author.id, ctx.guild.id)
                    await ctx.reply(embed=emb)
                    async with self.session() as session:
                        async with session.begin():
                            user = await session.execute(
                                select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                            )
                            user = user.scalars().first()
                            if not user:
                                return

                            user_stats: UserStats = user.users_stats[0]
                            user_stats.three_sevens_count += 1
                            user_stats.three_sevens_loses_count += 1
                            user_stats.entire_amount_of_winnings -= bid
                            user_stats.all_loses_count += 1
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['coinflip'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __casino_2(self, ctx: commands.context.Context, count: int = None, member: discord.Member = None):
        date_now = get_time()
        color = get_color(ctx.author.roles)
        if self._is_the_casino_allowed(ctx.message.channel.id):
            if member is None:
                if await self._check_cash(ctx, count, min_cash=10, check=True):
                    await self._take_coins(ctx.author.id, ctx.guild.id, count)
                    casino_num = casino2ch(ctx.author.id)[0]
                    if casino_num == 1:
                        emb = discord.Embed(title="Вы выиграли!", colour=color)
                        emb.add_field(
                            name=f'Поздравляем!',
                            value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(count * 2)}** DP коинов!',
                            inline=False
                        )
                        await self._add_win(ctx.author.id, ctx.guild.id)
                        await ctx.reply(embed=emb)
                        await self._add_coins(ctx.author.id, ctx.guild.id, count * 2)
                        async with self.session() as session:
                            async with session.begin():
                                user = await session.execute(
                                    select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                )
                                user = user.scalars().first()
                                if not user:
                                    return
                                user_stats: UserStats = user.users_stats[0]
                                user_stats.coin_flips_count += 1
                                user_stats.coin_flips_wins_count += 1
                                user_stats.entire_amount_of_winnings += count
                                user_stats.all_wins_count += 1
                    else:
                        emb = discord.Embed(title="Вы проиграли:(", colour=color)
                        emb.add_field(
                            name=f'Вы проиграли:(',
                            value=f'{ctx.author.mention}, значит в следующий раз',
                            inline=False
                        )
                        await self._add_lose(ctx.author.id, ctx.guild.id)
                        await ctx.reply(embed=emb)
                        async with self.session() as session:
                            async with session.begin():
                                user = await session.execute(
                                    select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                )
                                user = user.scalars().first()
                                if not user:
                                    return
                                user_stats: UserStats = user.users_stats[0]
                                user_stats.coin_flips_count += 1
                                user_stats.coin_flips_losses_count += 1
                                user_stats.entire_amount_of_winnings -= count
                                user_stats.all_loses_count += 1

            elif member is not None:
                if count <= 9:
                    await ctx.reply(f"{ctx.author.mention}, Вы не можете поставить ставку меньше 10")
                elif ctx.author.id == member.id:
                    await ctx.reply("Вы не можете играть с самим собой")
                elif count is None:
                    await ctx.reply(f"{ctx.author.mention}, Вы не ввели вашу ставку")
                elif self._get_cash(ctx.author.id, ctx.guild.id) < count:
                    await ctx.reply(f"{ctx.author.mention}, У Вас недостаточно средств")
                elif self._get_cash(member.id, ctx.guild.id) < count:
                    await ctx.reply(f"{ctx.author.mention}, У Вашего оппонента недостаточно средств")
                else:
                    async with self.session() as session:
                        coin_flips = await session.execute(
                            select(CoinFlip).where(
                                (
                                    CoinFlip.first_player_id == ctx.author.id
                                    and
                                    CoinFlip.second_player_id == member.id)
                                or
                                (
                                    CoinFlip.first_player_id == member.id
                                    and
                                    CoinFlip.second_player_id == ctx.author.id
                                )
                            )
                        )
                    coin_flips = coin_flips.scalars().first()
                    if coin_flips:
                        await ctx.reply(
                            f"{ctx.author.mention}, такая игра уже существует! Для удаления - "
                            f"{PREFIX}del_games "
                            f"{member.mention}"
                        )
                    async with self.session() as session:
                        async with session.begin():
                            new_coin_flip = CoinFlip()
                            new_coin_flip.guild_id = ctx.guild.id
                            new_coin_flip.first_player_id = ctx.author.id
                            new_coin_flip.second_player_id = member.id
                            new_coin_flip.cash = count
                            new_coin_flip.date = str(date_now)
                            session.add(new_coin_flip)

                    emb = discord.Embed(title=f"{member}, вас упомянули в коинфлипе!", colour=color)
                    emb.add_field(
                        name=f'Коинфлип на {count} DP коинов!',
                        value=f"{ctx.author.mention}, значит в следующий раз"
                              f"{PREFIX}accept {ctx.author.mention}\n\nЧтобы отменить - "
                              f"{PREFIX}reject {ctx.author.mention}",
                        inline=False
                    )
                    await ctx.reply(embed=emb)
                    await ctx.reply(member.mention)
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=["roll"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __roll(self, ctx: commands.context.Context, count: int = None, *args):
        color = get_color(ctx.author.roles)
        count = count
        if self._is_the_casino_allowed(ctx.message.channel.id):
            if await self._check_cash(ctx, count, min_cash=10, check=True):
                self.texts[ctx.author.id] = ""
                self.casino[ctx.author.id] = {}
                self.casino[ctx.author.id]["color"] = choice(
                    "black", "red", shuffle_long=37, key=str(ctx.author.id), array_long=37
                )
                self.casino[ctx.author.id]["number"] = (random.randint(0, 36), )
                # TODO: fix indexes
                # casino2[ctx.author.id]["number"] = 1, [random.randint(0, 36), random.randint(0, 36)]
                for i in args:
                    self.texts[ctx.author.id] += i
                try:
                    self.casino[ctx.author.id]["color"][0] = casino_numbers_color[
                        self.casino[ctx.author.id]["number"][0]
                    ]
                    if int(self.texts[ctx.author.id][0]) < 0:
                        pass
                    elif int(self.texts[ctx.author.id][0]) > 36:
                        pass
                    else:
                        await self._take_coins(ctx.author.id, ctx.guild.id, count)
                        if int(self.texts[ctx.author.id]) == 0 and int(self.texts[ctx.author.id][0]) \
                                == self.casino[ctx.author.id]["number"][0]:
                            count *= 35
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value='Выпало число {}, green\n{}'
                                      ", Вы выиграли **{}** DP коинов!!".format(
                                            self.casino[ctx.author.id]['number'][0],
                                            ctx.author.mention,
                                            divide_the_number(count)
                                        ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 35
                                    user_stats.all_wins_count += 1

                        elif int(self.texts[ctx.author.id]) == self.casino[ctx.author.id]["number"][0]:
                            count *= 35
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 35
                                    user_stats.all_wins_count += 1
                        else:
                            emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=color)
                            emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы  проиграли:(".format(
                                            self.casino[ctx.author.id]['number'][0],
                                            self.casino[ctx.author.id]['color'][0],
                                            ctx.author.mention
                                        ),
                                inline=False)
                            await self._add_lose(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_loses_count += 1
                                    user_stats.entire_amount_of_winnings -= count
                                    user_stats.all_loses_count += 1
                except ValueError:
                    if self.texts[ctx.author.id] in roll_types:
                        await self._take_coins(ctx.author.id, ctx.guild.id, count)
                        if self.texts[ctx.author.id] == "1st12" and self.casino[ctx.author.id]["number"][0] <= 12:
                            count *= 3
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 3
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "2nd12" and \
                                24 >= self.casino[ctx.author.id]["number"][0] > 12:
                            count *= 3
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 3
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "3rd12" and self.casino[ctx.author.id]["number"][0] > 24:
                            count *= 3
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 3
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "1to18" and \
                                0 != self.casino[ctx.author.id]["number"][0] <= 18:
                            count *= 2
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count / 2
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "19to36" and \
                                18 < self.casino[ctx.author.id]["number"][0] <= 36:
                            count *= 2
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count / 2
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "2to1" and self.casino[ctx.author.id]["number"][0] in row1:
                            count *= 3
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await ctx.reply(embed=emb)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 3
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "2to2" and self.casino[ctx.author.id]["number"][0] in row2:
                            count *= 3
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 3
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "2to3" and self.casino[ctx.author.id]["number"][0] in row3:
                            count *= 3
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count - count / 3
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "b" and self.casino[ctx.author.id]["color"][0] == "black":
                            count *= 2
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count / 2
                                    user_stats.all_wins_count += 1

                        elif self.texts[ctx.author.id] == "r" and self.casino[ctx.author.id]["color"][0] == "red":
                            count *= 2
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=color)
                            emb.add_field(
                                name=f'Поздравляем!',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count / 2
                                    user_stats.all_wins_count += 1
                        elif self.texts[ctx.author.id] == "ch" and self.casino[ctx.author.id]["number"][0] % 2 == 0:
                            count *= 2
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return
                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count / 2
                                    user_stats.all_wins_count += 1
                        elif self.texts[ctx.author.id] == "nch" and self.casino[ctx.author.id]["number"][0] % 2 == 1:
                            count *= 2
                            await self._add_coins(ctx.author.id, ctx.guild.id, count)
                            emb = discord.Embed(title="Вы выиграли!", colour=color)
                            emb.add_field(
                                name=f'🎰Поздравляем!🎰',
                                value="Выпало число {}, {}\n{}, Вы выиграли **{}** DP коинов!".format(
                                    self.casino[ctx.author.id]["number"][0],
                                    self.casino[ctx.author.id]["color"][0],
                                    ctx.author.mention, divide_the_number(count)
                                ),
                                inline=False)
                            await self._add_win(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return

                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_wins_count += 1
                                    user_stats.entire_amount_of_winnings += count / 2
                                    user_stats.all_wins_count += 1
                        else:
                            emb = discord.Embed(title="🎰Вы проиграли:(🎰", colour=color)
                            emb.add_field(
                                name=f'Сочувствую...',
                                value="Выпало число {}, {}"
                                      "\n{}, Вы проиграли:(".format(
                                            self.casino[ctx.author.id]['number'][0],
                                            self.casino[ctx.author.id]['color'][0],
                                            ctx.author.mention
                                        ),
                                inline=False)
                            await self._add_lose(ctx.author.id, ctx.guild.id)
                            await ctx.reply(embed=emb)
                            async with self.session() as session:
                                async with session.begin():
                                    user = await session.execute(
                                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                                    )
                                    user = user.scalars().first()
                                    if not user:
                                        return

                                    user_stats: UserStats = user.users_stats[0]
                                    user_stats.rolls_count += 1
                                    user_stats.rolls_loses_count += 1
                                    user_stats.entire_amount_of_winnings -= count
                                    user_stats.all_loses_count += 1

                    else:
                        await ctx.reply(f"{ctx.author.mention}, Такого атрибута не существует! ")
        else:
            await ctx.reply(f"{ctx.author.mention}, Вы можете играть в казино только в специальном канале!")

    @commands.command(aliases=['del_games'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __del_games(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            async with self.session() as session:
                async with session.begin():
                    coin_flips = await session.execute(
                        select(CoinFlip).where(
                            CoinFlip.first_player_id == ctx.author.id or CoinFlip.second_player_id == ctx.author.id
                        )
                    )
                    await session.execute(
                        delete(coin_flips)
                    )
            await ctx.message.add_reaction('✅')
        else:
            if not (ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723):
                await ctx.reply("Ты чё ку-ку? Тебе так нельзя.")
            async with self.session() as session:
                async with session.begin():
                    coin_flips = await session.execute(
                        select(CoinFlip).where(
                            CoinFlip.first_player_id == member.id or CoinFlip.second_player_id == member.id
                        )
                    )
                    await session.execute(
                        delete(coin_flips)
                    )
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=['reject'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __reject(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            await ctx.reply("Вы не ввели человека")
            return
        if member.id == ctx.author.id:
            await ctx.reply("Вы не можете ввести себя")
            return
        async with self.session() as session:
            games = await session.execute(
                select(
                    CoinFlip
                ).where(
                    (CoinFlip.first_player_id == ctx.author.id and CoinFlip.second_player_id == member.id)
                    or
                    (CoinFlip.first_player_id == member.id and CoinFlip.second_player_id == ctx.author.id)
                )
            )

        if not games.scalars().first():
            await ctx.reply(
                f"Такой игры не существует, посмотреть все ваши активные игры - {PREFIX}games"
            )
            return
        async with self.session() as session:
            async with session.begin():
                await session.execute(
                    delete(games)
                )
        await ctx.message.add_reaction('✅')

    @commands.command(aliases=['games'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __games(self, ctx: commands.context.Context):
        async with self.session() as session:
            games = await session.execute(
                select(CoinFlip).where(
                    CoinFlip.first_player_id == ctx.author.id
                    or
                    CoinFlip.second_player_id == ctx.author.id
                )
            )
        if not games.scalars().first():
            await ctx.reply("У Вас нет активных игр")
        emb = discord.Embed(title="Активные коинфлипы")
        for row in games.scalars():

            emb.add_field(
                name=f'{self.bot.get_user(row.first_player_id).name} и {self.bot.get_user(row.second_player_id).name}',
                value=f'Сумма: {row.cash}',
                inline=False
            )
        await ctx.reply(embed=emb)

    @commands.command(aliases=['accept'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def __c_accept(self, ctx: commands.context.Context, member: discord.Member = None):
        if member is None:
            await ctx.reply("Вы не ввели человека")
            return
        async with self.session() as session:
            coinflip = await session.execute(
                select(CoinFlip).where(
                    (CoinFlip.first_player_id == ctx.author.id and CoinFlip.second_player_id == member.id)
                    or
                    (CoinFlip.first_player_id == member.id and CoinFlip.second_player_id == ctx.author.id)
                )
            )
        coinflip = coinflip.scalars().first()
        if not coinflip:
            await ctx.reply(
                f"Такой игры не существует, посмотреть все ваши активные игры - {PREFIX}games"
            )
            return
        if total_minutes(coinflip.date) > 5:
            await ctx.reply(f"Время истекло:(")

            async with self.session() as session:
                async with session.begin():
                    await session.execute(
                        delete(coinflip)
                    )
            return
        if self._get_cash(coinflip.first_player_id, ctx.guild.id) < coinflip.cash:
            await ctx.reply(f"{self.bot.get_user(coinflip.first_player_id).mention}, У Вас недостаточно средств!")
            return
        if self._get_cash(coinflip.second_player_id, ctx.guild.id) < coinflip.cash:
            await ctx.reply(f"{self.bot.get_user(coinflip.second_player_id).mention}, У Вас недостаточно средств!")
            return
        num = coinflip.cash
        await self._take_coins(ctx.author.id, ctx.guild.id, num)
        await self._take_coins(member.id, ctx.guild.id, num)
        self.ch = random.randint(1, 2)
        # if member.id == 401555829620211723:
        #       self.ch = 2
        if self.ch == 1:
            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
            emb.add_field(
                name=f'Поздравляем!',
                value=f'{ctx.author.mention}, Вы выиграли **{divide_the_number(num * 2)}** DP коинов!',
                inline=False
            )
            await ctx.reply(embed=emb)
            await self._add_coins(ctx.author.id, ctx.guild.id, num * 2)
            async with self.session() as session:
                async with session.begin():
                    first_user = await session.execute(
                        select(User).where(User.user_id == member.id and User.guild_id == ctx.guild.id)
                    )
                    second_user = await session.execute(
                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                    )
                    first_user: User = first_user.scalars().first()
                    second_user: User = second_user.scalars().first()
                    first_user.achievements[0].losses += 1
                    first_user.achievements[0].wins = 0

                    second_user.achievements[0].losses = 0
                    second_user.achievements[0].wins += 1
            await self._achievement(member.id, ctx.guild.id)
            await self._achievement(ctx.author.id, ctx.guild.id)
            async with self.session() as session:
                async with session.begin():
                    first_user = await session.execute(
                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                    )
                    second_user = await session.execute(
                        select(User).where(User.user_id == member.id and User.guild_id == ctx.guild.id)
                    )
                    first_user = first_user.scalars().first()
                    second_user = second_user.scalars().first()
                    if not first_user:
                        return
                    if not second_user:
                        return

                    first_user_stats: UserStats = first_user.users_stats[0]
                    first_user_stats.coin_flips_count += 1
                    first_user_stats.coin_flips_wins_count += 1
                    first_user_stats.entire_amount_of_winnings += num
                    first_user_stats.all_wins_count += 1

                    second_user_stats: UserStats = second_user.users_stats[0]
                    second_user_stats.coin_flips_count += 1
                    second_user_stats.coin_flips_losses_count += 1
                    second_user_stats.entire_amount_of_winnings -= num
                    second_user_stats.all_loses_count += 1
        else:
            await self._achievement(member.id, ctx.guild.id)
            await self._achievement(ctx.author.id, ctx.guild.id)
            emb = discord.Embed(title="🎰Вы выиграли!🎰", colour=get_color(ctx.author.roles))
            emb.add_field(
                name=f'Поздравляем!',
                value=f'{member.mention}, Вы выиграли **{divide_the_number(num * 2)}** DP коинов!',
                inline=False
            )
            await ctx.reply(embed=emb)
            await self._add_coins(member.id, member.guild.id, num * 2)
            async with self.session() as session:
                async with session.begin():
                    first_user = await session.execute(
                        select(User).where(User.user_id == member.id and User.guild_id == ctx.guild.id)
                    )
                    second_user = await session.execute(
                        select(User).where(User.user_id == ctx.author.id and User.guild_id == ctx.guild.id)
                    )
                    first_user = first_user.scalars().first()
                    second_user = second_user.scalars().first()
                    if not first_user:
                        return
                    if not second_user:
                        return

                    first_user_stats: UserStats = first_user.users_stats[0]
                    first_user_stats.coin_flips_count += 1
                    first_user_stats.coin_flips_wins_count += 1
                    first_user_stats.entire_amount_of_winnings += num
                    first_user_stats.all_wins_count += 1

                    second_user_stats: UserStats = second_user.users_stats[0]
                    second_user_stats.coin_flips_count += 1
                    second_user_stats.coin_flips_losses_count += 1
                    second_user_stats.entire_amount_of_winnings -= num
                    second_user_stats.all_loses_count += 1
        async with self.session() as session:
            async with session.begin():
                coin_flips = await session.execute(
                    select(CoinFlip).where(
                        (CoinFlip.first_player_id == ctx.author.id and CoinFlip.second_player_id == member.id)
                        or
                        (CoinFlip.first_player_id == member.id and CoinFlip.second_player_id == ctx.author.id)
                    )
                )
            await session.execute(
                delete(coin_flips)
            )
