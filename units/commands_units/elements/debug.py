# -*- coding: utf-8 -*-
import logging
import os
import smtplib

from discord import File
from discord.ext import commands
from typing import Callable
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.user.cards import Card
from units.additions import (
    get_time, write_log
)
from units.json_logging import Json
from config import (
    BOT_EMAIL,
    DEBUG_EMAIL,
    PASSWORD
)

__all__ = (
    "Debug",
)


class Debug(commands.Cog):
    NAME = 'debug module'

    def __init__(self, bot: commands.Bot, session, *args, **kwargs) -> None:
        self.encoder = kwargs["encoder"]
        del kwargs["encoder"]
        super().__init__(*args, **kwargs)

        self.session: Callable[[], AsyncSession] = session
        self.bot: commands.Bot = bot
        self.file_path: str = ".intermediate_files/debug_send.txt"
        logging.info(f"Debug connected")

    @commands.command(aliases=["debug"])
    async def __debug_logs(
            self, ctx: commands.context.Context, count: int = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if not os.path.exists(".intermediate_files"):
                os.mkdir(".intermediate_files")
            with open(
                    ".logs/develop_logs.dpcb", encoding="utf-8", errors="ignore"
            ) as read_file, \
                    open(
                        ".intermediate_files/debug_send.txt", "w+", encoding="utf-8", errors="ignore"
                    ) as write_file:
                lines = read_file.readlines()
                if count is None:
                    count = 5
                for i in range(count, 0, -1):
                    try:
                        write_file.write(f"[{get_time()}] [INFO]: " + lines[-i])
                    except IndexError:
                        for j in range(len(lines)):
                            write_file.write(f"[{get_time()}] [INFO]: " + lines[j])
                        break
            await ctx.reply(f"**debug logs**\nname:{os.name}\nusername: {os.getlogin()}\ndate: {get_time()}\n",
                            file=File(".intermediate_files/debug_send.txt"))
            os.remove(self.file_path)

    @commands.command(aliases=['send_base'])  # это лучше не трогать
    async def __bd_send(self, ctx: commands.context.Context) -> None:
        if ctx.author.id == 401555829620211723:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open('database/server.db', "rb").read())
            encoders.encode_base64(part)

            part.add_header(
                'Content-Disposition',
                "attachment; filename= %s" % os.path.basename('database/server.db')
            )
            msg = MIMEMultipart()
            msg['From'] = self.encoder.decrypt(BOT_EMAIL)
            msg['To'] = self.encoder.decrypt(DEBUG_EMAIL)
            msg['Subject'] = "База данных"
            msg.attach(part)
            msg.attach(MIMEText("База данных за {}".format(str(get_time()))))
            server = smtplib.SMTP('smtp.gmail.com: 587')
            server.starttls()
            server.login(
                msg['From'],
                self.encoder.decrypt(PASSWORD)
            )
            server.sendmail(
                msg['From'],
                msg['To'],
                msg.as_string()
            )
            server.quit()
            write_log("[{}] [INFO]: База данных отправлена на почту".format(str(get_time())))
            await ctx.reply("Копия бд отправлена на почту")

        else:
            await ctx.reply("У Вас недостаточно прав")

    @commands.command(aliases=["card_add"])
    async def __card_add(
            self, ctx: commands.context.Context, user_id: int = 0, type_of_card: str = None
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                if ctx.author.id == 401555829620211723:
                    user: Card = await session.execute(
                        select(Card).where(
                            Card.user_id == user_id
                        )
                    )
                    user = user.scalars().first()
                    if type_of_card == "gg":
                        user.verification = 1
                    elif type_of_card == "bg":
                        user.verification = 2
                    elif type_of_card == "dv":
                        user.developer = 1
                    elif type_of_card == "cd":
                        user.coder = 1
                    elif type_of_card == "coin":
                        user.coin = 1
                    await ctx.message.add_reaction('✅')

    @commands.command(aliases=["card_remove"])
    async def __card_remove(
            self, ctx: commands.context.Context, user_id: int = 0, type_of_card: str = None
    ) -> None:
        async with self.session() as session:
            async with session.begin():
                if ctx.author.id == 401555829620211723:
                    user: Card = await session.execute(
                        select(Card).where(
                            Card.user_id == user_id
                        )
                    )
                    user = user.scalars().first()
                    if type_of_card == "gg":
                        user.verification = 0
                    elif type_of_card == "bg":
                        user.verification = 0
                    elif type_of_card == "dv":
                        user.developer = 0
                    elif type_of_card == "cd":
                        user.coder = 0
                    elif type_of_card == "coin":
                        user.coin = 0
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
                        js = {"lb": True, "slb": True}
                    else:
                        js = Json(".json/develop_get.json").json_load()
                    if arg == "on":
                        arg = True
                    else:
                        arg = False
                    js[place] = arg
                    Json(".json/develop_get.json").json_dump(js)

    @commands.command(aliases=['add_to_ban_list'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __add_ban_list(
            self, ctx: commands.context.Context, server_id: int = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if not Json.check_file_exists(".json/ban_list.json"):
                Json(".json/ban_list.json").json_dump([])
            else:
                data = Json(".json/ban_list.json").json_load()
                data.append(server_id)
                Json(".json/ban_list.json").json_dump(data)

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
        print(error)
        # raise error
        if isinstance(error, commands.CommandOnCooldown):
            pass
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            raise error
            logging.error(error)
            try:
                write_log(f"error: {str(ctx.author)} ({ctx.author.id}) "
                          f"({ctx.guild.id})\t {str(error)}\t{str(get_time())}\n")
            except AttributeError:
                pass
