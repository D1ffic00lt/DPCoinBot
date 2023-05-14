# -*- coding: utf-8 -*-
import logging
from typing import Callable

import discord
import random

from datetime import datetime

import numpy as np
from discord.ext import commands
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from toxicityclassifier import ToxicityClassificator

from bot import DPCoinBot
from config import DATE_FORMAT
from database.bot.levels import Level
from database.user.online import Online
from database.user.online_stats import OnlineStats
from database.user.users import User
from units.additions import get_time, datetime_to_str

from units.json_logging import Json

__all__ = (
    "Events",
)


class Events(commands.Cog):
    NAME = 'events module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session: Callable[[], AsyncSession] = session
        self.bot: DPCoinBot = bot
        self.model = ToxicityClassificator()
        self.last_message = {}
        self.prises = {}
        self.valentine = {}
        logging.info(f"Events connected")

    async def _voice_create(
            self, user_id: int, guild_id: int, voice_create_stats: bool = False
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                if voice_create_stats:
                    await self._insert_into_online_stats(user_id, guild_id)
                online = Online()
                online.user_id = guild_id
                online.user_id = user_id
                online.time = get_time()
                session.add(online)

    async def _insert_into_online_stats(self, user_id: int, guild_id: int) -> None:
        async with self.session() as session:
            async with session.begin():
                online_stats = OnlineStats()
                online_stats.user_id = user_id
                online_stats.guild_id = guild_id
                online_stats.time = get_time()
                session.add(online_stats)

    async def _voice_delete(self, member: discord.Member, arg: bool = True) -> None:
        async with self.session() as session:
            async with session.begin():
                online_stats = await session.execute(
                    select(OnlineStats).where(
                        OnlineStats.user_id == member.id and OnlineStats.guild_id == member.guild.id
                    )
                )
                online_stats: OnlineStats = online_stats.scalars().first()
                user = await session.execute(
                    select(User).where(
                        User.user_id == member.id and User.guild_id == member.guild.id
                    )
                )
                user: User = user.scalars().first()
                try:
                    now2 = online_stats.time
                except TypeError:
                    pass
                else:
                    minutes = int((datetime_to_str(get_time()) - now2).total_seconds() // 60)
                    user.cash += minutes
                    user.users_stats[0].minutes_in_voice_channels += minutes
                    await session.execute(
                        delete(Online).where(Online.user_id == member.id)
                    )
                    month = int(datetime.today().strftime('%m'))
                    day = int(datetime.today().strftime('%d'))
                    if month > 11 or month == 1:
                        if (month == 12 and day > 10) or (month == 1 and day < 15):
                            self.prises[member.id] = 0
                            for i in range(minutes):
                                if len(set(np.random.randint(1, 6, 5))) == 3 and \
                                        len(set(np.random.randint(1, 6, 5))) == 3:
                                    self.prises[member.id] += 1
                            if self.prises[member.id] != 0:
                                user.inventories[0].new_year_prises += self.prises[member.id]
                                try:
                                    await member.send(
                                        "Вам начислено {} новогодних подарков! Чтобы открыть их пропишите //open\n"
                                        "У нас кстати новогодний ивент:) пиши //help new_year".format(
                                            self.prises[member.id]
                                        )
                                    )
                                except discord.errors.Forbidden:
                                    pass
                    if month == 2 and day == 14:
                        self.valentine[member.id] = 0
                        for i in range(minutes):
                            if len(set(np.random.randint(1, 6, 5))) == 3 and len(set(np.random.randint(1, 6, 5))) == 3:
                                self.valentine[member.id] += 1
                        if self.valentine[member.id] != 0:
                            user.inventories[0].valentines += self.valentine[member.id]
                            try:
                                await member.send(
                                    "Вам пришло {} валентинок! Чтобы открыть их пропишите //val_open".format(
                                        self.valentine[member.id]
                                    )
                                )
                            except discord.errors.Forbidden:
                                pass
                    if arg:
                        online_stats = OnlineStats()
                        online_stats.guild_id = member.guild.id
                        online_stats.user_id = member.id
                        online_stats.time = get_time()
                        session.add(online_stats)

    async def _voice_delete_stats(self, member: discord.Member, arg: bool = True) -> None:
        async with self.session() as session:
            async with session.begin():
                online_stats = await session.execute(
                    select(OnlineStats).where(
                        OnlineStats.user_id == member.id and OnlineStats.guild_id == member.guild.id
                    )
                )
                online_stats: OnlineStats = online_stats.scalars().first()
                user = await session.execute(
                    select(User).where(
                        User.user_id == member.id and User.guild_id == member.guild.id
                    )
                )
                user: User = user.scalars().first()
                try:
                    now2 = online_stats.time
                except TypeError:
                    pass
                else:
                    time = int((datetime_to_str(get_time()) - now2).total_seconds() // 60)
                    await session.execute(
                        delete(OnlineStats).where(OnlineStats.user_id == member.id)
                    )
                    user.users_stats[0].minutes_in_voice_channels += time

                    if arg is True:
                        online_stats = OnlineStats()
                        online_stats.user_id = member.id
                        online_stats.guild_id = member.guild.id
                        online_stats.time = get_time()
                        session.add(online_stats)
                    minutes = user.users_stats[0].minutes_in_voice_channels
                    if minutes >= 1 and user.achievements[0].voice_achievements_level < 1:
                        user.achievements[0].voice_achievements_level = 1
                        user.cash += 500
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «Вроде они добрые...»!\nВам начислено 500 коинов!"
                        )
                    if minutes >= 10 and user.achievements[0].voice_achievements_level == 2:
                        user.achievements[0].voice_achievements_level = 2
                        user.cash += 700
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «Они добрые!»!\nВам начислено 700 коинов!"
                        )
                    if minutes >= 100 and user.achievements[0].voice_achievements_level < 3:
                        user.achievements[0].voice_achievements_level = 3
                        user.cash += 1500
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «Отличная компания»!\nВам начислено 1500 коинов!"
                        )
                    if minutes >= 1000 and user.achievements[0].voice_achievements_level < 4:
                        user.achievements[0].voice_achievements_level = 4
                        user.cash += 3000
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «А они точно добрые?»!\nВам начислено 3000 коинов!"
                        )
                    if minutes >= 10000 and user.achievements[0].voice_achievements_level < 5:
                        user.achievements[0].voice_achievements_level = 5
                        user.cash += 7000
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «СПАСИТЕ»!\nВам начислено 7000 коинов!"
                        )
                    if minutes >= 100000 and user.achievements[0].voice_achievements_level < 6:
                        user.achievements[0].voice_achievements_level = 6
                        user.cash += 14000
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «А может и не надо...»!\nВам начислено 14000 коинов!"
                        )
                    if minutes >= 1000000 and user.achievements[0].voice_achievements_level < 7:
                        user.achievements[0].voice_achievements_level = 7
                        user.cash += 28000
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «Всё-таки они хорошие:)»!\nВам начислено 28000 коинов!"
                        )
                    if minutes >= 10000000 and user.achievements[0].voice_achievements_level < 8:
                        user.achievements[0].voice_achievements_level = 8
                        user.cash += 58000
                        await member.send(
                            f"На сервере {member.guild} "
                            f"получено достижение «А у меня есть личная жизнь?»!\nВам начислено 58000 коинов!"
                        )

    @commands.Cog.listener()
    async def on_voice_state_update(
            self, member: discord.Member,
            before: discord.VoiceChannel.type,
            after: discord.VoiceChannel.type
    ) -> None:
        member_guild_afk_channel_id = 0 if member.guild.afk_channel is None else member.guild.afk_channel.id
        channel_into_which_the_member_entered = 0 if after.channel is None else after.channel.id
        the_channel_from_which_the_member_came_out = 0 if before.channel is None else before.channel.id
        if not member.bot:
            if not before.channel and after.channel and \
                    member_guild_afk_channel_id != channel_into_which_the_member_entered:
                await self._voice_create(member.id, member.guild.id)
                await self._insert_into_online_stats(member.id, member.guild.id)
            elif before.channel and after.channel:
                if member_guild_afk_channel_id == channel_into_which_the_member_entered:
                    await self._voice_delete(member, False)
                    await self._voice_delete_stats(member, False)
                elif member_guild_afk_channel_id == the_channel_from_which_the_member_came_out:
                    await self._voice_create(member.id, member.guild.id, voice_create_stats=True)
                elif channel_into_which_the_member_entered == the_channel_from_which_the_member_came_out:
                    if after.self_mute:
                        await self._voice_delete(member, False)
                        await self._voice_delete_stats(member)
                    elif not after.self_mute and before.self_mute:
                        await self._voice_create(member.id, member.guild.id)
                        await self._voice_delete_stats(member)
                else:
                    await self._voice_delete(member)
                    await self._voice_delete_stats(member)
            elif before.channel and not after.channel:
                await self._voice_delete(member, False)
                await self._voice_delete_stats(member, False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        async with self.session() as session:
            async with session.begin():
                if message.guild is not None:
                    if message.guild.id in Json.get_ban_list():
                        await self.bot.get_guild(message.guild.id).leave()
                user = await session.execute(
                    select(User).where(User.user_id == message.author.id and User.guild_id == message.guild.id)
                )
                user: User = user.scalars().first()
                if not user:
                    await self.bot.add_server()
                month = int(datetime.today().strftime('%m'))
                day = int(datetime.today().strftime('%d'))
                if not Json.check_file_exists(".json/last_save.json"):
                    Json(".json/last_save.json").json_dump(
                        {
                            "day": day,
                            "month": month
                        }
                    )
                else:
                    data = Json(".json/last_save.json").json_load()
                    if (day > data["day"] and month == data["month"]) or \
                            (day < data["day"] and month > data["month"]) or \
                            (month == 1 and day == 1 and day < data["day"]):
                        # self.db.send_files()
                        Json(".json/last_save.json").json_dump(
                            {
                                "day": day,
                                "month": month
                            }
                        )
                await self.bot.process_commands(message)
                try:  # когда-нибудь я это уберу
                    if self.last_message[message.author.id] is None:
                        self.last_message[message.author.id] = {"message": "", "date": get_time()}
                except KeyError:
                    self.last_message[message.author.id] = {"message": "", "date": get_time()}
                if not message.author.bot:
                    if message.author is not None and message.guild is not None and message.content not in ["", None]:
                        # logging.info(self.model.get_probability(message.content))
                        user.users_stats[0].reputation += self.model.get_probability(message.content)
                    time = datetime.strptime(
                        datetime.now().strftime(DATE_FORMAT),
                        DATE_FORMAT
                    ) - datetime.strptime(
                        self.last_message[message.author.id]["date"],
                        DATE_FORMAT
                    )

                    index = random.randint(1, 3)
                    text = message.content.lower()

                    time = datetime.now() - time
                    time = time.second

                    if text != self.last_message[message.author.id]["message"]:
                        self.last_message[message.author.id]["message"] = text
                        if len(text) > 7 and message.author is not None and message.guild is not None:
                            user.users_stats[0].messages_count += 1
                            if time > 60 or time == 0:
                                user.users_stats[0].xp += random.randint(1, 15)
                                xp = user.users_stats[0].xp
                                level_in_chat = user.users_stats[0].chat_lvl
                                levels = await session.execute(
                                    select(Level)
                                )
                                levels = levels.scalars().all()
                                for level in levels:
                                    if level.xp <= xp and level.level > level_in_chat:
                                        user.users_stats[0].chat_lvl += 1
                                        user.cash += level.award
                                        try:
                                            await message.author.send(
                                                f"{message.author.mention}, поздравляем с {level.level} левелом!\n"
                                                f"Вот "
                                                f"тебе "
                                                f"немного коинов! (**{level.award}**)\n"
                                                f"{xp} опыта всего"
                                            )
                                        except discord.errors.Forbidden:
                                            pass

                                        break
                            self.last_message[message.author.id]["date"] = get_time()
                            if index == 1 and message.author is not None and message.guild is not None:
                                level = user.users_stats[0].chat_lvl
                                if level != 1:
                                    if level != 5:
                                        level *= 2
                                    else:
                                        level *= 4
                                user.cash += level

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self.bot.add_server()
        logging.info(f"{member} add to the database")
