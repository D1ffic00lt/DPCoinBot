from __future__ import annotations

import os
import smtplib

import discord
import vk_api
import requests

from typing import Any
from discord import File, Webhook, RequestsWebhookAdapter
from discord.ext import commands
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from vk_api import VkApi

from .helperfunction import (
    get_time, write_msg, get_color,
    create_emb, write_log, logging
)
from .texts import *
from .json_ import Json
from ..database.db import Database
from ..config import settings
from ..version import __version__


class Debug(commands.Cog, name='debug module', Database):
    @logging
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__("server.db")
        self.bot: commands.Bot = bot
        self.js: dict[Any]
        self.data: list[int | dict]
        self.part: MIMEBase
        self.msg: MIMEMultipart
        self.server: smtplib.SMTP
        self.arg: bool
        self.color: discord.Color
        print("Debug connected")

    @commands.command(aliases=["debug"])
    async def __debug_logs(
            self,
            ctx: commands.context.Context,
            count: int = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            with open("logs/develop_logs.dpcb", encoding="utf-8", errors="ignore") as read_file, \
                    open("prom_files/debug_send.txt", "w+", encoding="utf-8", errors="ignore") as write_file:
                self.lines = read_file.readlines()
                if count is None:
                    count = 5
                for i in range(count, 0, -1):
                    try:
                        write_file.write(self.lines[-i])
                    except IndexError:
                        for j in range(len(self.lines)):
                            write_file.write(self.lines[j])
                        break
            await ctx.send(f"**debug logs**\nname:{os.name}\nusername: {os.getlogin()}\ndate: {get_time()}\n",
                           file=File("prom_files/debug_send.txt"))
            file_path = "prom_files/debug_send.txt"
            os.remove(file_path)

    @commands.command(aliases=['send_base'])  # это лучше не трогать
    async def __bd_send(self, ctx: commands.context.Context) -> None:
        if ctx.author.id == 401555829620211723:
            self.part = MIMEBase('application', "octet-stream")
            self.part.set_payload(open('server.db', "rb").read())
            encoders.encode_base64(self.part)

            self.part.add_header(
                'Content-Disposition',
                "attachment; filename= %s" % os.path.basename('../database/server.db')
            )
            self.msg = MIMEMultipart()
            self.msg['From'] = settings["sender_email"]
            self.msg['To'] = settings["to_send_email"]
            self.msg['Subject'] = "База данных"
            self.msg.attach(self.part)
            self.msg.attach(MIMEText("База данных за {}".format(str(get_time()))))
            self.server = smtplib.SMTP('smtp.gmail.com: 587')
            self.server.starttls()
            self.server.login(
                self.msg['From'],
                settings["password"]
            )
            self.server.sendmail(
                self.msg['From'],
                self.msg['To'],
                self.msg.as_string()
            )
            self.server.quit()
            write_log("\nБаза данных отправлена на почту\tдата: {}\n\n".format(str(get_time())))
            await ctx.send("Копия бд отправлена на почту")

        else:
            await ctx.send("У Вас недостаточно прав")

    @commands.command(aliases=["card_add"])
    async def __card_add(
            self,
            ctx: commands.context.Context,
            user_id: int = 0,
            type_of_card: str = None
    ) -> None:
        if ctx.author.id == 401555829620211723 and self.check_user(user_id):
            if type_of_card == "gg":
                self.update_card(user_id, "Verification", 1)
                await ctx.message.add_reaction('✅')
            elif type_of_card == "bg":
                self.update_card(user_id, "Verification", 2)
                await ctx.message.add_reaction('✅')
            elif type_of_card == "dv":
                self.update_card(user_id, "Developer", 1)
                await ctx.message.add_reaction('✅')
            elif type_of_card == "cd":
                self.update_card(user_id, "Coder", 1)
            await ctx.message.add_reaction('✅')

    @commands.command(aliases=["card_remove"])
    async def __card_remove(
            self,
            ctx: commands.context.Context,
            user_id: int = 0,
            param: str = None
    ) -> None:
        if ctx.author.id == 401555829620211723 and self.check_user(user_id):
            if param == "gg":
                self.update_card(user_id, "Verification", 0)
                await ctx.message.add_reaction('✅')
            elif param == "bg":
                self.update_card(user_id, "Verification", 0)
                await ctx.message.add_reaction('✅')
            elif param == "dv":
                self.update_card(user_id, "Developer", 0)
                await ctx.message.add_reaction('✅')
            elif param == "cd":
                self.update_card(user_id, "Coder", 0)
                await ctx.message.add_reaction('✅')

    @commands.command(aliases=['develop_stats'])
    async def __develop_stats(
            self,
            ctx: commands.context.Context,
            place: str = None,
            arg: str = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if place is not None and arg is not None:
                if place in ["lb", "slb"] and arg in ["on", "off"]:
                    if not os.path.exists(".json/develop_get.json"):
                        Json("develop_get.json").json_dump({"lb": True, "slb": True})
                        self.js = {"lb": True, "slb": True}
                    else:
                        self.js = Json("develop_get.json").json_load()
                    if arg == "on":
                        self.arg = True
                    else:
                        self.arg = False
                    self.js[place] = self.arg
                    Json("develop_get.json").json_dump(self.js)

    @commands.command(aliases=['add_to_ban_list'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __add_ban_list(
            self,
            ctx: commands.context.Context,
            server_id: int = None
    ) -> None:
        if ctx.author.id == 401555829620211723:
            if not os.path.exists("../.json/ban_list.json"):
                Json("ban_list.json").json_dump([])
            else:
                self.data = Json("ban_list.json").json_load()
                self.data.append(server_id)
                Json("ban_list.json").json_dump(self.data)

    @commands.command(aliases=['send_webhook'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __send_webhook(self, ctx: commands.context.Context, par: str = None) -> None:
        if ctx.author.id == 401555829620211723:
            if par == "push":
                self.webhook = Webhook.from_url(
                    "https://discord.com/api/webhooks/798442296265408542/" + settings["webhook"],
                    adapter=RequestsWebhookAdapter()
                )
                requests.post(
                    'https://api.vk.com/method/wall.post', data={
                        'access_token': settings["token"],
                        'owner_id': settings["owner_id_group"],
                        'from_group': 1,
                        'message': foo,
                        'signed': 0,
                        'v': "5.52"
                    }
                ).json()
                if not os.path.exists("../.json/send.json") or os.stat("../.json/send.json").st_size == 0:
                    Json("send.json").json_dump([])
                else:
                    self.js = Json("send.json").json_load()
                    if len(self.js) != 0:
                        self.vk: VkApi = vk_api.VkApi(token=settings["vk_token"])
                        self.vk.auth_token()
                        # self.vk.auth_token()
                        # немного изменили код VkApi, переименовав функцию, так как она вызывает ошибку pep8
                        for i in self.js:
                            try:
                                write_msg(i, f"Обновление {__version__}! Быстрее смотреть!\n{foo}", self.vk)
                            except vk_api.exceptions.ApiError:
                                pass

            else:
                self.webhook = Webhook.from_url(
                    "https://discord.com/api/webhooks/798211458352939008/" + settings["test_webhook"],
                    adapter=RequestsWebhookAdapter()
                )
            self.color = get_color(ctx.author.roles)
            self.webhook.send(
                embed=create_emb(
                    title="Обновление DPcoin BOT",
                    color=self.color, args=[
                        {
                            "name": f'Версия {__version__}',
                            "value": discord_foo,
                            "inline": False
                        }
                    ]
                )
            )

    @commands.Cog.listener()
    async def on_command_error(
            self,
            ctx: commands.context.Context,
            error: Exception
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
