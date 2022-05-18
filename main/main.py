from templates.helperfunction import *
from config import *
from version import __version__
from bot import DPcoinBOT
from templates.casino import Casino
from templates.debug import Debug

def main() -> None:
    BOT = DPcoinBOT(
        command_prefix=settings["prefix"],
        intents=discord.Intents.all()
    )

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(
        f"{settings['prefix']}help"))

    # if not os.path.exists("json_/ban_list.json"):
    #     with open('json_/last_save.json', 'w+') as outfile:
    #         json.dump([], outfile)

    print("Bot connected")
    print("version: {}\n".format(__version__))
    BOT.add_cog(Casino(BOT))
    BOT.add_cog(Debug(BOT))
    BOT.run(settings["token"])


if __name__ == '__main__':
    main()
