import logging

import discord
import random

from datetime import datetime
from discord.ext import commands
from typing import Union
from toxicityclassifier import ToxicityClassificator

from config import DATE_FORMAT
from modules.additions import (
    get_time, write_log
)
from modules.json_ import Json
from database.db import Database

__all__ = (
    "Events",
)


class Events(commands.Cog):
    NAME = 'events module'

    __slots__ = (
        "time", "day", "month", "db", "level", "index",
        "data", "xp", "level_in_chat", "ban_list", "bot",
        "member_guild_afk_channel_id", "channel_into_which_the_member_entered",
        "the_channel_from_which_the_member_came_out", "last_message", "text"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.text: str = ""
        self.level: int = 0
        self.index: int = 0
        self.month: int = 0
        self.day: int = 0
        self.xp: int = 0
        self.level_in_chat: int = 0
        self.member_guild_afk_channel_id: int = 0
        self.channel_into_which_the_member_entered: int = 0
        self.the_channel_from_which_the_member_came_out: int = 0
        self.time: Union[datetime, int] = 0
        self.data: dict = {}
        self.last_message: dict = {}
        self.ban_list: list = []
        self.bot = bot
        self.model = ToxicityClassificator()
        print(f"[{get_time()}] [INFO]: Events connected")
        write_log(f"[{get_time()}] [INFO]: Events connected")

    @commands.Cog.listener()
    async def on_voice_state_update(
            self, member: discord.Member,
            before: discord.VoiceChannel.type,
            after: discord.VoiceChannel.type
    ) -> None:
        self.member_guild_afk_channel_id = 0 if member.guild.afk_channel is None else member.guild.afk_channel.id
        self.channel_into_which_the_member_entered = 0 if after.channel is None else after.channel.id
        self.the_channel_from_which_the_member_came_out = 0 if before.channel is None else before.channel.id
        if not member.bot:
            if not before.channel and after.channel and \
                    self.member_guild_afk_channel_id != self.channel_into_which_the_member_entered:
                self.db.voice_create(member.id, member.guild.id)
                self.db.insert_into_online_stats(member.id, member.guild.id)
            elif before.channel and after.channel:
                if self.member_guild_afk_channel_id == self.channel_into_which_the_member_entered:
                    await self.db.voice_delete(member, False)
                    await self.db.voice_delete_stats(member, False)
                elif self.member_guild_afk_channel_id == self.the_channel_from_which_the_member_came_out:
                    self.db.voice_create(member.id, member.guild.id, voice_create_stats=True)
                elif self.channel_into_which_the_member_entered == self.the_channel_from_which_the_member_came_out:
                    if after.self_mute:
                        await self.db.voice_delete(member, False)
                        await self.db.voice_delete_stats(member, True)
                    elif not after.self_mute and before.self_mute:
                        self.db.voice_create(member.id, member.guild.id)
                        await self.db.voice_delete_stats(member, True)
                else:
                    await self.db.voice_delete(member, True)
                    await self.db.voice_delete_stats(member, True)
            elif before.channel and not after.channel:
                await self.db.voice_delete(member, False)
                await self.db.voice_delete_stats(member, False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is not None:
            if message.guild.id in Json.get_ban_list():
                await self.bot.get_guild(message.guild.id).leave()
        if not self.db.check_user(message.author.id):
            self.db.server_add(self.bot)
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if not Json.check_file_exists(".json/last_save.json"):
            Json(".json/last_save.json").json_dump(
                {
                    "day": self.day,
                    "month": self.month
                }
            )
        else:
            self.data = Json(".json/last_save.json").json_load()
            if (self.day > self.data["day"] and self.month == self.data["month"]) or \
                    (self.day < self.data["day"] and self.month > self.data["month"]) or \
                    (self.month == 1 and self.day == 1 and self.day < self.data["day"]):
                # self.db.send_files()
                Json(".json/last_save.json").json_dump(
                    {
                        "day": self.day,
                        "month": self.month
                    }
                )
        await self.bot.process_commands(message)
        try:  # когда-нибудь я это уберу
            if self.last_message[message.author.id] is None:
                self.last_message[message.author.id] = {"message": "", "date": get_time()}
        except KeyError:
            self.last_message[message.author.id] = {"message": "", "date": get_time()}
        if not message.author.bot:
            if message.author is not None and message.guild is not None:
                # print(self.model.get_probability(message.content))
                self.db.add_reputation(
                    message.author.id,
                    message.guild.id,
                    self.model.get_probability(message.content)
                )
            self.time = datetime.strptime(
                datetime.now().strftime(DATE_FORMAT),
                DATE_FORMAT
            ) - datetime.strptime(
                self.last_message[message.author.id]["date"],
                DATE_FORMAT
            )

            self.index = random.randint(1, 3)
            self.text = message.content.lower()

            self.time = datetime.now() - self.time
            self.time = self.time.second

            if self.text != self.last_message[message.author.id]["message"]:
                self.last_message[message.author.id]["message"] = self.text
                if len(self.text) > 7 and message.author is not None and message.guild is not None:
                    self.db.update_stat(message.author.id, message.guild.id, "MessagesCount", 1)
                    if self.time > 60 or self.time == 0:
                        self.db.update_stat(message.author.id, message.guild.id, "Xp", random.randint(1, 15))
                        self.xp = self.db.get_stat(message.author.id, message.guild.id, "Xp")
                        self.level_in_chat = self.db.get_stat(message.author.id, message.guild.id, "ChatLevel")
                        for i in self.db.get_from_levels("XP", "Level", "Award"):
                            if i[0] <= self.xp and i[1] > self.level_in_chat:
                                self.db.update_stat(message.author.id, message.guild.id, "ChatLevel", 1)
                                self.db.add_coins(message.author.id, message.guild.id, i[2])
                                try:
                                    await message.author.send(
                                        f"{message.author.mention}, поздравляем с {i[1]} левелом!\n"
                                        f"Вот "
                                        f"тебе "
                                        f"немного коинов! (**{i[2]}**)\n"
                                        f"Опыта для следующего левела - **{self.db.get_xp(i[1] + 1) - self.xp}**, "
                                        f"{self.xp} опыта "
                                        f"всего")
                                except discord.errors.Forbidden:
                                    pass

                                break
                    self.last_message[message.author.id]["date"] = get_time()
                    if self.index == 1 and message.author is not None and message.guild is not None:
                        self.level = self.db.get_level(message.author.id, message.guild.id)
                        if self.level != 1:
                            if self.level != 5:
                                self.level *= 2
                            else:
                                self.level *= 4
                        self.db.add_coins(message.author.id, message.guild.id, self.level)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        self.db.server_add(self.bot)
        print(f"[{get_time()}] [INFO]: {member.id} add to the database")
        write_log(f"[{get_time()}] [INFO]: {member.id} add to the database")
