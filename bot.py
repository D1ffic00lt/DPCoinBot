# -*- coding: utf-8 -*-
import math
import discord

from discord.ext import commands

from botsections.functions.config import settings
from botsections.functions.helperfunction import logging
from database.db import Database


class DPcoinBOT(commands.Bot):
    __slots__ = (
        "lvl", "db"
    )

    def __init__(self, command_prefix: str, **kwargs) -> None:
        super().__init__(command_prefix, **kwargs)
        self.lvl: int = 0
        self.db: Database = kwargs["db"]
        self.remove_command('help')

    @logging
    async def on_ready(self) -> None:
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"{settings['prefix']}help")
        )
        self.db.server_add(self)
        if not self.db.checking_for_levels_existence_in_table():
            self.lvl = 1
            for i in range(1, 405):
                self.db.insert_into_levels(i, int(math.pow((self.lvl * 32), 1.4)), i * int(math.pow(self.lvl, 1.2)))
                self.lvl += 1
            self.db.cursor.execute("UPDATE `Levels` SET `Award` = 1500000 WHERE `Level` = 404")
            self.db.connection.commit()

        self.db.clear_coinflip()
        print("Bot connected")
