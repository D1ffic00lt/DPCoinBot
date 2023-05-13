# -*- coding: utf-8 -*-
import logging
import discord
import math

from discord.ext import commands
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio.session import AsyncSession
from config import PREFIX
from typing import Callable

from database.user.online_stats import OnlineStats
from database.user.online import Online
from database.user.users import User
from database.user.cards import Card
from database.user.achievements import Achievement
from database.user.inventories import Inventory
from database.bot.new_year_event import NewYearEvent
from database.bot.levels import Level
from database.bot.coinflips import CoinFlip
from database.guild.guilds import Guild
from database.guild.servers import ServerSettings


class DPcoinBOT(commands.Bot):
    __slots__ = (
        "lvl", "session"
    )

    def __init__(self, command_prefix: str, *, intents: discord.Intents, **kwargs) -> None:
        super().__init__(command_prefix, intents=intents, **kwargs)
        self.session: Callable[[], AsyncSession] = kwargs["db"]
        self.remove_command('help')

    async def on_ready(self) -> None:
        await self.wait_until_ready()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"{PREFIX}help")
        )
        session = self.session()
        for guild in self.guilds:
            discord_guild = await session.execute(select(Guild).where(Guild.guild_id == guild.id))
            if not discord_guild.scalars().first():
                new_guild = Guild()
                new_guild.guild_id = guild.id
                new_guild.members = guild.member_count
                session.add(new_guild)
                await session.commit()

            server_guild = await session.execute(select(ServerSettings).where(ServerSettings.guild_id == guild.id))
            if not server_guild.scalars().first():
                start_cash = 0
            else:
                start_cash = await session.execute(
                    select(ServerSettings).where(ServerSettings.guild_id == guild.id)
                )
                start_cash = start_cash.scalars().first()[0].starting_balance
            for member in guild.members:
                guild_member = await session.execute(
                        select(User).where(User.user_id == member.id and User.guild_id == guild.id)
                )
                if not guild_member.scalars().first():
                    new_user = User()
                    new_user.user_id = member.id
                    new_user.guild_id = guild.id
                    new_user.cash = start_cash
                    session.add(new_user)
                    await session.commit()

                    card = Card()
                    card.user_id = member.id
                    session.add(card)

                    achievements = Achievement()
                    achievements.guild_id = guild.id
                    achievements.user_id = member.id
                    session.add(card)

                    inventory = Inventory()
                    inventory.guild_id = guild.id
                    inventory.user_id = member.id
                    session.add(inventory)

                    new_year_event = NewYearEvent()
                    new_year_event.guild_id = guild.id
                    new_year_event.user_id = member.id

                    await session.commit()

            if not session.get(Level, 1):
                lvl = 1
                for i in range(1, 405):
                    level = Level()
                    level.level = i
                    level.xp = int(math.pow((lvl * 32), 1.4))
                    level.award = i * int(math.pow(lvl, 1.2))
                    session.add(level)
                    lvl += 1
                max_level = await session.execute(select(Level).where(Level.level == 404))
                max_level = max_level.scalars().first()[0]
                max_level.award = 1500000

                await session.execute(delete(OnlineStats))
                await session.execute(delete(Online))
                await session.execute(delete(CoinFlip))
                await session.commit()

        logging.info(f"Bot connected")
