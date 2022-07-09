# -*- coding: utf-8 -*-
import math
import discord

from discord.ext import commands

from botsections.config import settings
from botsections.database.db import Database
from botsections.helperfunction import logging


class DPcoinBOT(commands.Bot):
    def __init__(self, command_prefix: str, **kwargs):
        super().__init__(command_prefix, **kwargs)
        self.db: Database = Database("server.db")
        self.remove_command('help')

    @logging
    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"{settings['prefix']}help")
        )
        self.db.server_add(self)
        if not self.db.checking_for_levels_existence_in_table():
            lvl = 1
            for i in range(1, 405):
                self.db.insert_into_levels(i, int(math.pow((lvl * 32), 1.4)), i * int(math.pow(lvl, 1.2)))
                lvl += 1
            self.db.cursor.execute("UPDATE levels SET award = 1500000 WHERE level = 404")
            self.db.connection.commit()

        self.db.clear_coinflip()
        print("Bot connected")
