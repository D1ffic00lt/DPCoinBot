# -*- coding: utf-8 -*-
from bot import DPcoinBOT
from templates.admin import Admin
from templates.casino import Casino
from templates.debug import Debug
from templates.events import Events
from templates.guild import Guild
from templates.json_ import Json
from templates.user import User
from templates.helperfunction import *
from version import __version__

print("\n" + "Program started" + "\n")


@logging
def main() -> None:
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(
        f"{settings['prefix']}help"))

    if not Json.check_file_exists("ban_list.json"):
        Json("../.json/ban_list.json").json_dump([])

    BOT.add_cog(Casino(BOT))
    BOT.add_cog(Debug(BOT))
    BOT.add_cog(User(BOT))
    BOT.add_cog(Events(BOT))
    BOT.add_cog(Guild(BOT))
    BOT.add_cog(Admin(BOT))

    BOT.run(settings["token"])
    print("Bot connected")
    print("version: {}\n".format(__version__))


if __name__ == '__main__':
    main()
