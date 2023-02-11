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
from modules.json_ import Json
from modules.encoding import Encoder
from slashbotsections import *
from config import (
    PREFIX, TOKEN,
    FORMAT, DATE_FORMAT,
    LOG_PATH, __version__,
    TESTING_MODE, TESTERS_PREFIX
)

logging.basicConfig(format=FORMAT, datefmt=DATE_FORMAT, level=logging.INFO)
handler = logging.FileHandler(LOG_PATH, mode='+a')
handler.setFormatter(logging.Formatter(FORMAT))
logging.getLogger().addHandler(handler)

warnings.filterwarnings("ignore")
nest_asyncio.apply()

logging.info("Program started")


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

    logging.info(f"Encoder connected")
    db = Database("database/server.db", encoder=encoder)
    logging.info(f"Database connected")
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=PREFIX if not TESTING_MODE else TESTERS_PREFIX,
        intents=intents,
        db=db, case_insensitive=True
    )
    logging.info("version: {}".format(__version__))

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
        logging.error(error, exc_info=True)
