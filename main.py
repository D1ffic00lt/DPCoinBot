# -*- coding: utf-8 -*-
import os
import warnings
import discord
import nest_asyncio
import logging

from asyncio import run

from bot import DPCoinBot
from database.session import create_session, global_init
from units import *
from units.json_logging import Json
from units.encoding import Encoder
from config import (
    PREFIX, TOKEN,
    FORMAT, DATE_FORMAT,
    LOG_PATH, __version__,
    TESTING_MODE, TESTERS_PREFIX,
    GPT_TOKEN
)

logging.basicConfig(format=FORMAT, datefmt=DATE_FORMAT, level=logging.INFO)
if not os.path.isdir(LOG_PATH.split("/")[0]):
    os.mkdir(LOG_PATH.split("/")[0])
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
    await global_init("database/server.db")
    logging.info(f"Database connected")

    BOT: DPCoinBot = DPCoinBot(
        command_prefix=PREFIX if not TESTING_MODE else TESTERS_PREFIX,
        intents=intents,
        db=create_session, case_insensitive=True
    )
    logging.info("version: {}".format(__version__))

    await BOT.add_cog(Casino(BOT, create_session))
    await BOT.add_cog(Debug(BOT, create_session, encoder=encoder))
    await BOT.add_cog(User(BOT, create_session, encoder.decrypt(GPT_TOKEN)))
    await BOT.add_cog(Events(BOT, create_session))
    await BOT.add_cog(Guild(BOT, create_session))
    await BOT.add_cog(Admin(BOT, create_session))
    await BOT.add_cog(Public(BOT))
    await BOT.add_cog(NewYear(BOT, create_session))
    await BOT.add_cog(ValentinesDay(BOT, create_session))

    await BOT.add_cog(CasinoSlash(BOT, create_session))
    await BOT.add_cog(UserSlash(BOT, create_session, encoder.decrypt(GPT_TOKEN)))
    await BOT.add_cog(GuildSlash(BOT, create_session))
    await BOT.add_cog(AdminSlash(BOT, create_session))
    await BOT.add_cog(PublicSlash(BOT))
    await BOT.add_cog(NewYearSlash(BOT, create_session))
    await BOT.add_cog(ValentinesDaySlash(BOT, create_session))

    BOT.run(encoder.decrypt(TOKEN))

if __name__ == '__main__':
    try:
        runner = run(main())
    except Exception as error:
        logging.error(error, exc_info=True)
