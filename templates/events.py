from __future__ import annotations

import discord
import random

from datetime import datetime
from discord.ext import commands

from .helperfunction import (
    write_log,
    get_time,
    logging
)
from .json_ import Json
from ..database.db import Database


class Debug(commands.Cog, name='debug module', Database):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.level: int = 0
        self.index: int = 0
        self.data: dict = {}
        self.month: int
        self.day: int
        self.xp: int = 0
        self.level_in_chat: int = 0
        self.ban_list: list = []
        self.bot: commands.Bot = bot
        self.member_guild_afk_channel_id: int = 0
        self.channel_into_which_the_member_entered: int = 0
        self.the_channel_from_which_the_member_came_out: int = 0
        self.last_message: dict = {}
        self.text: str = ""
        self.time: datetime

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
                self.voice_create(member.id, member.guild.id)
                self.voice_create_stats(member.id, member.guild.id)
            elif before.channel and after.channel:
                if self.member_guild_afk_channel_id == self.channel_into_which_the_member_entered:
                    await self.voice_delete(member, False)
                    await self.voice_delete_stats(member, False)
                elif self.member_guild_afk_channel_id == self.the_channel_from_which_the_member_came_out:
                    self.voice_create(member.id, member.guild.id, voice_create_stats=True)
                elif self.channel_into_which_the_member_entered == self.the_channel_from_which_the_member_came_out:
                    if after.self_mute:
                        await self.voice_delete(member, False)
                        await self.voice_delete_stats(member, True)
                    elif not after.self_mute and before.self_mute:
                        self.voice_create(member.id, member.guild.id)
                        await self.voice_delete_stats(member, True)
                else:
                    await self.voice_delete(member, True)
                    await self.voice_delete_stats(member, True)
            elif before.channel and not after.channel:
                await self.voice_delete(member, False)
                await self.voice_delete_stats(member, False)

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.guild is not None:
            if not Json.check_file_exists("ban_list.json"):
                Json("ban_list.json").json_dump([])
            if message.guild.id in Json.get_ban_list():
                await self.bot.get_guild(message.guild.id).leave()
        if not self.check_user(message.author.id):
            self.server_add(self.bot)
        self.month = int(datetime.today().strftime('%m'))
        self.day = int(datetime.today().strftime('%d'))
        if not Json.check_file_exists("last_save.json"):
            Json("last_save.json").json_dump(
                {
                    "day": self.day,
                    "month": self.month
                }
            )
        else:
            self.data = Json("last_save.json").json_load()
            if (self.day > self.data["day"] and self.month == self.data["month"]) or \
                    (self.day < self.data["day"] and self.month > self.data["month"]) or \
                    (self.month == 1 and self.day == 1 and self.day < self.data["day"]):
                self.send_files()
                Json("last_save.json").json_dump(
                    {
                        "day": self.day,
                        "month": self.month
                    }
                )
        await self.bot.process_commands(message)
        try:
            if self.last_message[message.author.id] is None:
                self.last_message[message.author.id] = {"message": "", "date": get_time()}
        except KeyError:
            self.last_message[message.author.id] = {"message": "", "date": get_time()}
        if not message.author.bot:
            self.time = datetime.strptime(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "%Y-%m-%d %H:%M:%S"
            ) - datetime.strptime(
                self.last_message[message.author.id]["date"],
                "%Y-%m-%d %H:%M:%S"
            )

            self.index = random.randint(1, 3)
            self.text = message.content.lower()

            self.time = datetime.now() - self.time
            self.time = self.time.second

            if self.text != self.last_message[message.author.id]["message"]:
                self.last_message[message.author.id]["message"] = self.text
                if len(self.text) > 7 and message.author is not None and message.guild is not None:
                    self.update_stat(message.author.id, message.guild.id, "MessagesCount", 1)
                    if self.time > 60 or self.time == 0:
                        self.update_stat(message.author.id, message.guild.id, "Xp", random.randint(1, 15))
                        self.xp = self.get_stat(message.author.id, message.guild.id, "Xp")
                        self.level_in_chat = self.get_stat(message.author.id, message.guild.id, "ChatLevel")
                        for i in self.get_from_levels("XP", "Level", "Award"):
                            if i[0] <= self.xp and i[1] > self.level_in_chat:
                                self.update_stat(message.author.id, message.guild.id, "ChatLevel", 1)
                                self.add_coins(message.author.id, message.guild.id, i[2])
                                try:
                                    await message.author.send(
                                        f"{message.author.mention}, поздравляем с {i[1]} левелом!\n"
                                        f"Вот "
                                        f"тебе "
                                        f"немного коинов! (**{i[2]}**)\n"
                                        f"Опыта для следующего левела - **{self.get_xp(i[1] + 1) - self.xp}**, "
                                        f"{self.xp} опыта "
                                        f"всего")
                                except discord.errors.Forbidden:
                                    pass

                                break
                    self.last_message[message.author.id]["date"] = get_time()
                    if self.index == 1 and message.author is not None and message.guild is not None:
                        self.level = self.get_level(message.author.id, message.guild.id)
                        if self.level != 1:
                            if self.level != 5:
                                self.level *= 2
                            else:
                                self.level *= 4
                        self.add_coins(message.author.id, message.guild.id, self.level)

                    elif self.index == 2 and message.author is not None and message.guild is not None:
                        self.add_reputation(message.author.id, message.guild.id, 1)

    @logging
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        self.server_add()
        print(f"{member.id} add")

    @commands.Cog.listener()
    async def on_command_error(
            self,
            ctx: commands.context.Context,
            error: Exception
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            pass
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)
            try:
                write_log(f"error: {str(ctx.author)} ({ctx.author.id}) "
                          f"({ctx.guild.id})\t {str(error)}\t{str(get_time())}\n")
            except AttributeError:
                pass
