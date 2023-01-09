# -*- coding: utf-8 -*-
import os
import warnings
import discord
import nest_asyncio
import logging

from asyncio import run

from bot import DPcoinBOT
from database.db import Database
from botsections import *
from config import PREFIX, TOKEN, FORMAT
from modules.json_ import Json
from modules.version import __version__
from modules.additions import get_time, write_log
from modules.encoding import Encoder
from slashbotsections import *

warnings.filterwarnings("ignore")
logging.basicConfig(format=FORMAT)
nest_asyncio.apply()

print(f"[{get_time()}] [INFO]: Program started")
write_log(f"[{get_time()}] [INFO]: Program started")


async def main() -> None:
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True

    if not os.path.exists(".json"):
        os.mkdir(".json")
    if not Json.check_file_exists(".json/ban_list.json"):
        Json(".json/ban_list.json").json_dump([])
    if not os.path.exists(".json/key.dpcb"):    # тут его как-то с сервера получать надо
        raise FileExistsError("not found key.dpcb")
    if not os.path.exists(".intermediate_files"):
        os.mkdir(".intermediate_files")
        os.mkdir(".intermediate_files/images")
    if not os.path.exists(".intermediate_files/images"):
        os.mkdir(".intermediate_files/images")

    with open(".json/key.dpcb", "rb") as file:
        encoder = Encoder(file.read())

    print(f"[{get_time()}] [INFO]: Encoder connected")
    write_log(f"[{get_time()}] [INFO]: Encoder connected")
    db = Database("database/server.db", encoder=encoder)
    print(f"[{get_time()}] [INFO]: Database connected")
    write_log(f"[{get_time()}] [INFO]: Database connected")
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=PREFIX,
        intents=intents,
        db=db, case_insensitive=True
    )
    print("[{}] [INFO]: version: {}".format(get_time(), __version__))
    write_log("[{}] [INFO]: version: {}".format(get_time(), __version__))

    await BOT.add_cog(Casino(BOT, db))
    await BOT.add_cog(Debug(BOT, db, encoder=encoder))
    await BOT.add_cog(User(BOT, db))
    await BOT.add_cog(Events(BOT, db))
    await BOT.add_cog(Guild(BOT, db))
    await BOT.add_cog(Admin(BOT, db))
    await BOT.add_cog(Public(BOT, db))
    await BOT.add_cog(NewYear(BOT, db))
    await BOT.add_cog(ValentinesDay(BOT, db))

    await BOT.add_cog(CasinoSlash(BOT, db))
    await BOT.add_cog(UserSlash(BOT, db))
    await BOT.add_cog(GuildSlash(BOT, db))
    await BOT.add_cog(AdminSlash(BOT, db))
    await BOT.add_cog(PublicSlash(BOT, db))
    await BOT.add_cog(NewYearSlash(BOT, db))
    await BOT.add_cog(ValentinesDaySlash(BOT, db))

    BOT.run(encoder.decrypt(TOKEN))

if __name__ == '__main__':
    try:
        runner = run(main())
    except Exception as error:
        logging.error(error)
