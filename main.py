# -*- coding: utf-8 -*-
from bot import DPcoinBOT
from botsections.admin import Admin
from botsections.casino import Casino
from botsections.debug import Debug
from botsections.events import Events
from botsections.guild import Guild
from botsections.json_ import Json
from botsections.public import Public
from botsections.user import User
from botsections.helperfunction import *
from botsections.config import settings
from botsections.version import __version__

print("Program started")


@logging
def main() -> None:
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )
    print("version: {}".format(__version__))
    if not Json.check_file_exists("ban_list.json"):
        Json("ban_list.json").json_dump([])

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
