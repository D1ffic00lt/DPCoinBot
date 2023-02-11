# -*- coding: utf-8 -*-
import logging
import discord
import math

from discord.ext import commands

from config import PREFIX
from database.db import Database


class DPcoinBOT(commands.Bot):
    __slots__ = (
        "lvl", "db"
    )

    def __init__(self, command_prefix: str, *, intents: discord.Intents, **kwargs) -> None:
        super().__init__(command_prefix, intents=intents, **kwargs)
        self.db: Database = kwargs["db"]
        self.remove_command('help')

    async def on_ready(self) -> None:
        await self.wait_until_ready()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"{PREFIX}help")
        )
        self.db.server_add(self)
        if not self.db.checking_for_levels_existence_in_table():
            lvl = 1
            for i in range(1, 405):
                self.db.insert_into_levels(i, int(math.pow((lvl * 32), 1.4)), i * int(math.pow(lvl, 1.2)))
                lvl += 1
            self.db.cursor.execute("UPDATE `Levels` SET `Award` = 1500000 WHERE `Level` = 404")
            self.db.cursor.execute("DELETE FROM `OnlineStats`")
            self.db.cursor.execute("DELETE FROM `Online`")
            self.db.connection.commit()

        self.db.clear_coinflip()
        logging.info(f"Bot connected")
