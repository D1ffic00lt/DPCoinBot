# -*- coding: utf-8 -*-
import os
import discord
import nest_asyncio

from asyncio import run

from bot import DPcoinBOT
from database.db import Database
from botsections import *
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
    if not os.path.exists(".json/key.dpcb"):    # тут его как-то с сервера получать надо
        raise FileExistsError("not found key.txt")
    if not os.path.exists(".intermediate_files"):
        os.mkdir(".intermediate_files")
        os.mkdir(".intermediate_files/images")
    if not os.path.exists(".intermediate_files/images"):
        os.mkdir(".intermediate_files/images")

    with open(".json/key.dpcb", "rb") as file:
        encoder = Encoder(file.read())

    print("[{}] [INFO]: Encoder connected", file=logs)
    db = Database("database/server.db", encoder=encoder)
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
