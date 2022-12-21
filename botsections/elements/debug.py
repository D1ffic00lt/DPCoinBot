import os
import _io
import smtplib
import discord

from discord import File
from discord.ext import commands
from typing import Any, Union, List, Dict
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from botsections.functions.helperfunction import (
    get_time, write_log
)
from botsections.functions.json_ import Json
from botsections.functions.config import settings
from database.db import Database

__all__ = (
    "Debug",
)


class Debug(commands.Cog):
    NAME = 'debug module'

    __slots__ = (
        "db", "bot", "js", "data", "part",
        "msg", "server", "arg", "file_path",
        "color", "read_file",
        "write_file", "lines"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        self.encoder = kwargs["encoder"]
        del kwargs["encoder"]

        super().__init__(*args, **kwargs)

        self.db = db
        self.bot: commands.Bot = bot
        self.part: MIMEBase
        self.msg: MIMEMultipart
        self.server: smtplib.SMTP
        self.color: discord.Color
        self.js: Dict[Any]
        self.data: List[Union[dict, int]]
        self.arg: bool
        self.file_path: str = ".intermediate_files/debug_send.txt"
        self.lines: str
        self.read_file: _io.TextIOWrapper
        self.write_file: _io.TextIOWrapper
        print(f"[{get_time()}] [INFO]: Debug connected")
        write_log(f"[{get_time()}] [INFO]: Debug connected")

    @commands.command(aliases=["debug"])
    async def __debug_logs(
            self, ctx: commands.context.Context, count: int = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if not os.path.exists(".intermediate_files"):
                os.mkdir(".intermediate_files")
            with open(
                    ".logs/develop_logs.dpcb", encoding="utf-8", errors="ignore"
            ) as self.read_file, \
                    open(
                        ".intermediate_files/debug_send.txt", "w+", encoding="utf-8", errors="ignore"
                    ) as self.write_file:
                self.lines = self.read_file.readlines()
                if count is None:
                    count = 5
                for i in range(count, 0, -1):
                    try:
                        self.write_file.write(f"[{get_time()}] [INFO]: " + self.lines[-i])
                    except IndexError:
                        for j in range(len(self.lines)):
                            self.write_file.write(f"[{get_time()}] [INFO]: " + self.lines[j])
                        break
            await ctx.reply(f"**debug logs**\nname:{os.name}\nusername: {os.getlogin()}\ndate: {get_time()}\n",
                            file=File(".intermediate_files/debug_send.txt"))
            os.remove(self.file_path)

    @commands.command(aliases=['send_base'])  # это лучше не трогать
    async def __bd_send(self, ctx: commands.context.Context) -> None:
        if ctx.author.id == 401555829620211723:
            self.part = MIMEBase('application', "octet-stream")
            self.part.set_payload(open('database/server.db', "rb").read())
            encoders.encode_base64(self.part)

            self.part.add_header(
                'Content-Disposition',
                "attachment; filename= %s" % os.path.basename('database/server.db')
            )
            self.msg = MIMEMultipart()
            self.msg['From'] = self.encoder.decrypt(settings["sender_email"])
            self.msg['To'] = self.encoder.decrypt(settings["to_send_email"])
            self.msg['Subject'] = "База данных"
            self.msg.attach(self.part)
            self.msg.attach(MIMEText("База данных за {}".format(str(get_time()))))
            self.server = smtplib.SMTP('smtp.gmail.com: 587')
            self.server.starttls()
            self.server.login(
                self.msg['From'],
                self.encoder.decrypt(settings["password"])
            )
            self.server.sendmail(
                self.msg['From'],
                self.msg['To'],
                self.msg.as_string()
            )
            self.server.quit()
            write_log("[{}] [INFO]: База данных отправлена на почту".format(str(get_time())))
            await ctx.reply("Копия бд отправлена на почту")

        else:
            await ctx.reply("У Вас недостаточно прав")

    @commands.command(aliases=["card_add"])
    async def __card_add(
            self, ctx: commands.context.Context, user_id: int = 0, type_of_card: str = None
    ) -> None:
        if ctx.author.id == 401555829620211723 and self.db.check_user(user_id):
            if type_of_card == "gg":
                self.db.update_card(user_id, "Verification", 1)
                await ctx.message.add_reaction('✅')
            elif type_of_card == "bg":
                self.db.update_card(user_id, "Verification", 2)
                await ctx.message.add_reaction('✅')
            elif type_of_card == "dv":
                self.db.update_card(user_id, "Developer", 1)
                await ctx.message.add_reaction('✅')
            elif type_of_card == "cd":
                self.db.update_card(user_id, "Coder", 1)
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=["card_remove"])
    async def __card_remove(
            self, ctx: commands.context.Context, user_id: int = 0, param: str = None
    ) -> None:
        if ctx.author.id == 401555829620211723 and self.db.check_user(user_id):
            if param == "gg":
                self.db.update_card(user_id, "Verification", 0)
                await ctx.message.add_reaction('✅')
            elif param == "bg":
                self.db.update_card(user_id, "Verification", 0)
                await ctx.message.add_reaction('✅')
            elif param == "dv":
                self.db.update_card(user_id, "Developer", 0)
                await ctx.message.add_reaction('✅')
            elif param == "cd":
                self.db.update_card(user_id, "Coder", 0)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['develop_stats'])
    async def __develop_stats(
            self, ctx: commands.context.Context, place: str = None, arg: str = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if place is not None and arg is not None:
                if place in ["lb", "slb"] and arg in ["on", "off"]:
                    if not os.path.exists(".json/develop_get.json"):
                        Json(".json/develop_get.json").json_dump({"lb": True, "slb": True})
                        self.js = {"lb": True, "slb": True}
                    else:
                        self.js = Json(".json/develop_get.json").json_load()
                    if arg == "on":
                        self.arg = True
                    else:
                        self.arg = False
                    self.js[place] = self.arg
                    Json(".json/develop_get.json").json_dump(self.js)

    @commands.command(aliases=['add_to_ban_list'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __add_ban_list(
            self, ctx: commands.context.Context, server_id: int = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if not Json.check_file_exists(".json/ban_list.json"):
                Json(".json/ban_list.json").json_dump([])
            else:
                self.data = Json(".json/ban_list.json").json_load()
                self.data.append(server_id)
                Json(".json/ban_list.json").json_dump(self.data)

    @commands.command()
    async def sync(self, ctx: commands.context.Context, type_: str = "local"):
        if ctx.author.id == 401555829620211723:
            if type_ == "global":
                fmt = await ctx.bot.tree.sync()
                await ctx.reply(f"Synced {len(fmt)} (global)")
            else:
                fmt = await ctx.bot.tree.sync(guild=ctx.guild)
                await ctx.reply(f"Synced {len(fmt)}")
        else:
            await ctx.message.add_reaction('❌')

    @commands.Cog.listener()
    async def on_command_error(
            self, ctx: commands.context.Context, error: Exception
    ) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            pass
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(error)
            try:
                write_log(f"error: {str(ctx.author)} ({ctx.author.id}) "
                          f"({ctx.guild.id})\t {str(error)}\t{str(get_time())}\n")
            except AttributeError:
                pass
