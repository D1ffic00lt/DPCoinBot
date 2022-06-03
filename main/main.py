# -*- coding: utf-8 -*-
from DPcoinBOT.templates.helperfunction import *
from DPcoinBOT.config import *
from DPcoinBOT.version import __version__
from DPcoinBOT.main.bot import DPcoinBOT
from DPcoinBOT.templates.casino import Casino
from DPcoinBOT.templates.debug import Debug
from DPcoinBOT.templates.user import User
from DPcoinBOT.templates.json_ import Json
from DPcoinBOT.templates.events import Events


def main() -> None:
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(
        f"{settings['prefix']}help"))

    if not Json.check_file_exists("ban_list.json"):
        Json("../.json/ban_list.json").json_dump([])

    print("Bot connected")
    print("version: {}\n".format(__version__))

    BOT.add_cog(Casino(BOT))
    BOT.add_cog(Debug(BOT))
    BOT.add_cog(User(BOT))
    BOT.add_cog(Events(BOT))

    BOT.run(settings["token"])


if __name__ == '__main__':
    main()
