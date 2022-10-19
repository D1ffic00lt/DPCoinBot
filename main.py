# -*- coding: utf-8 -*-
import discord
import os

from bot import DPcoinBOT
from botsections.admin import Admin
from botsections.casino import Casino
from botsections.config import settings
from botsections.debug import Debug
from botsections.events import Events
from botsections.global_events.new_year import NewYear
from botsections.global_events.valentines_day import ValentinesDay
from botsections.guild import Guild
from botsections.helperfunction import logging
from botsections.json_ import Json
from botsections.public import Public
from botsections.user import User
from botsections.version import __version__
from botslashsections.admin_ import AdminSlash
from botslashsections.casino_ import CasinoSlash
from botslashsections.guild_ import GuildSlash
from botslashsections.public_ import PublicSlash
from botslashsections.user_ import UserSlash
from botslashsections.global_events.valentines_day_ import ValentinesDaySlash
from botslashsections.global_events.new_year_ import NewYearSlash

print("Program started")


@logging
def main() -> None:
    BOT: DPcoinBOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )
    print("version: {}".format(__version__))
    print(os.path)
    if not os.path.exists(".json"):
        os.mkdir(".json")
    if not Json.check_file_exists(".json/ban_list.json"):
        Json(".json/ban_list.json").json_dump([])

    BOT.add_cog(Casino(BOT))
    BOT.add_cog(Debug(BOT))
    BOT.add_cog(User(BOT))
    BOT.add_cog(Events(BOT))
    BOT.add_cog(Guild(BOT))
    BOT.add_cog(Admin(BOT))
    BOT.add_cog(Public(BOT))
    BOT.add_cog(NewYear(BOT))
    BOT.add_cog(ValentinesDay(BOT))
    BOT.add_cog(UserSlash(BOT))
    BOT.add_cog(AdminSlash(BOT))
    BOT.add_cog(GuildSlash(BOT))
    BOT.add_cog(CasinoSlash(BOT))
    BOT.add_cog(PublicSlash(BOT))
    BOT.add_cog(NewYearSlash(BOT))
    BOT.add_cog(ValentinesDaySlash(BOT))

    BOT.run(settings["token"])


if __name__ == '__main__':
    main()
