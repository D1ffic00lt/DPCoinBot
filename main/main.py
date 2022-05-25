# -*- coding: utf-8 -*-
import os

from templates.helperfunction import *
from config import *
from version import __version__
from bot import DPcoinBOT
from templates.casino import Casino
from templates.debug import Debug
from templates.user import User
from templates.json_ import Json


def main() -> None:
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(
        f"{settings['prefix']}help"))

    if not os.path.exists("../.json/ban_list.json"):
        Json("../.json/ban_list.json").json_dump([])

    print("Bot connected")
    print("version: {}\n".format(__version__))

    BOT.add_cog(Casino(BOT))
    BOT.add_cog(Debug(BOT))
    BOT.add_cog(User(BOT))
    BOT.run(settings["token"])


if __name__ == '__main__':
    main()
