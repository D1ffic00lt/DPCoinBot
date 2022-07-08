# -*- coding: utf-8 -*-
from bot import DPcoinBOT
from admin import Admin
from casino import Casino
from debug import Debug
from events import Events
from guild import Guild
from json_ import Json
from public import Public
from user import User
from helperfunction import *
from config import settings
from version import __version__

print("Program started")


@logging
def main() -> None:
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )
    print("version: {}".format(__version__))
    if not Json.check_file_exists("ban_list.json"):
        Json("../.json/ban_list.json").json_dump([])

    BOT.add_cog(Casino(BOT))
    BOT.add_cog(Debug(BOT))
    BOT.add_cog(User(BOT))
    BOT.add_cog(Events(BOT))
    BOT.add_cog(Guild(BOT))
    BOT.add_cog(Admin(BOT))
    BOT.add_cog(Public(BOT))

    BOT.run(settings["token"])


if __name__ == '__main__':
    main()
