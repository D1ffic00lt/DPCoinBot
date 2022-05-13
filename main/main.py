from DPcoinBOTs.DPcoinBOT2.templates.helperfunction import *
from DPcoinBOTs.DPcoinBOT2.config import *
from DPcoinBOTs.DPcoinBOT2.version import __version__
from DPcoinBOTs.DPcoinBOT2.main.bot import DPcoinBOT


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
    BOT.add_cog()
    BOT.run(settings["token"])


if __name__ == '__main__':
    main()
