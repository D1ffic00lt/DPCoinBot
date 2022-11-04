# -*- coding: utf-8 -*-
import os
import discord
import nest_asyncio

from asyncio import run

from bot import DPcoinBOT
from database.db import Database
from botsections.elements.admin import Admin
from botsections.elements.casino import Casino
from botsections.elements.debug import Debug
from botsections.elements.events import Events
from botsections.elements.public import Public
from botsections.elements.user import User
from botsections.elements.guild import Guild
from botsections.global_events.new_year import NewYear
from botsections.global_events.valentines_day import ValentinesDay
from botsections.functions.config import settings
from botsections.functions.json_ import Json
from botsections.functions.version import __version__
from botsections.functions.helperfunction import get_time, write_log
from botsections.functions.encoding import Encoder

write_log("")
logs = open(".logs/develop_logs.dpcb", "+a")

print(f"[{get_time()}]: [INFO]: Program started", file=logs)

nest_asyncio.apply()


async def main() -> None:
    if not os.path.exists(".json"):
        os.mkdir(".json")
    if not Json.check_file_exists(".json/ban_list.json"):
        Json(".json/ban_list.json").json_dump([])
    if not os.path.exists(".json/key.dpcb"):
        raise FileExistsError("not found key.txt")
    with open(".json/key.dpcb", "rb") as file:
        encoder = Encoder(file.read())

    print("[{}] [INFO]: Encoder connected", file=logs)
    db = Database("server.db", encoder=encoder)
    print(f"[{get_time()}] [INFO]: Database connected", file=logs)
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all(),
        db=db
    )
    print("[{}] [INFO]: version: {}".format(get_time(), __version__), file=logs)

    await BOT.add_cog(Casino(BOT, db))
    await BOT.add_cog(Debug(BOT, db, encoder=encoder))
    await BOT.add_cog(User(BOT, db))
    await BOT.add_cog(Events(BOT, db))
    await BOT.add_cog(Guild(BOT, db))
    await BOT.add_cog(Admin(BOT, db))
    await BOT.add_cog(Public(BOT, db))
    await BOT.add_cog(NewYear(BOT, db))
    await BOT.add_cog(ValentinesDay(BOT, db))

    BOT.run(encoder.decrypt(settings["token"]))
    logs.close()

if __name__ == '__main__':
    runner = run(main())
