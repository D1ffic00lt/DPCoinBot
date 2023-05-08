# -*- coding: utf-8 -*-
import logging
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

    __slots__ = (
        "db", "bot", "js", "data", "part",
        "msg", "server", "arg", "file_path",
        "color", "read_file",
        "write_file", "lines"
    )

    def __init__(self, bot: commands.Bot, db, *args, **kwargs) -> None:
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
            self.msg['From'] = self.encoder.decrypt(BOT_EMAIL)
            self.msg['To'] = self.encoder.decrypt(DEBUG_EMAIL)
            self.msg['Subject'] = "База данных"
            self.msg.attach(self.part)
            self.msg.attach(MIMEText("База данных за {}".format(str(get_time()))))
            self.server = smtplib.SMTP('smtp.gmail.com: 587')
            self.server.starttls()
            self.server.login(
                self.msg['From'],
                self.encoder.decrypt(PASSWORD)
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

    @commands.command(aliases=["send_message"])
    async def __card_add(
            self, ctx: commands.context.Context, publish: str = "no"
    ) -> None:
        if ctx.author.id != 401555829620211723:
            return
        self.emb1 = discord.Embed(
            title="Обновление 2.0.0!",
            description="Всех с Новым годом! В такой праздничный момент мы представляем Вам версию **2.0.0**!\n"
                        "Коротко об изменениях:"
        )
        self.emb1.set_image(
            url="https://media.discordapp.net/attachments/572705890524725248/1058749305890017352/dpbg1_3.png"
        )
        self.emb2 = discord.Embed(
            title="Удалено",
            description="Система увеличенного количества коинов за минуты в голосовых каналах в зависимости от уровня"
        )
        self.emb2.set_image(
            url="https://media.discordapp.net/attachments/572705890524725248/1058749306196197407/dpbg1_2.png"
        )
        self.emb3 = discord.Embed(
            title="Изменено",
            description="//rust_casino -> //wheel\n"
                        "Минимальный fail коэффициент 0.04 -> 0.07\n"
                        "Период \"дропа\" валентинок 1 день - > 4 дня\n"
                        "Максимальное количество коинов из валентинки 6000 -> 3000\n"
                        "Период \"дропа\" подарков 36 -> 41 (временно)\n"
                        "Переработана структура кода\n"
                        "Переработана структура базы данных"
        )
        self.emb3.set_image(
            url="https://media.discordapp.net/attachments/572705890524725248/1058749306506584134/dpbg1_.png"
        )
        self.emb4 = discord.Embed(
            title="Добавлено",
            description="**Встречайте слеш-команды!**\nБольшинство команд теперь можно использовать как слеш-команды!\n"
                        "**Полный список команд**:\n"
                        "</777:1058699153842114572>\n"
                        "</accept:1058699153842114578>\n"
                        "</add_rep:1058699154177663084>\n"
                        "</add-else:1058699154307682368>\n"
                        "</add-shop:1058699154307682367>\n"
                        "</auto_setup:1058699154257363020>\n"
                        "</bank:1058699154177663077>\n"
                        "</bug_report:1058699154257363019>\n"
                        "</buy:1058699154177663082>\n"
                        "</buy_food:1058699154307682373>\n"
                        "</buy_item:1058699154177663081>\n"
                        "</card:1058699154257363015>\n"
                        "</cash:1058699154177663076>\n"
                        "</coinflip:1058699153842114573>\n"
                        "</del_games:1058699153842114575>\n"
                        "</fail:1058699153842114571>\n"
                        "</food:1058699154509013066>\n"
                        "</foodshop:1058699154509013065>\n"
                        "</games:1058699153842114577>\n"
                        "</gift:1058699154257363017>\n"
                        "</give:1058699154257363022>\n"
                        "</give-role:1058699154307682364>\n"
                        "</help:1058699154307682371>\n"
                        "</info:1058699154307682370>\n"
                        "</lb:1058699154177663079>\n"
                        "</open:1058699154509013063>\n"
                        "</presents:1058699154509013064>\n"
                        "</promo:1058699154257363016>\n"
                        "</promos:1058699154257363018>\n"
                        "</reject:1058699153842114576>\n"
                        "</remove_rep:1058699154177663085>\n"
                        "</remove-else:1058699154307682369>\n"
                        "</remove-shop:1058699154307682366>\n"
                        "</roll:1058699153842114574>\n"
                        "</send:1058699154177663083>\n"
                        "</send_present:1058699154509013062>\n"
                        "</shop:1058699154177663080>\n"
                        "</slb:1058699154177663078>\n"
                        "</start_money:1058699154257363021>\n"
                        "</stats:1058699154257363014>\n"
                        "</take:1058699154257363023>\n"
                        "</take-role:1058699154307682365>\n"
                        "</update:1058699153842114579>\n"
                        "</use:1058699154307682372>\n"
                        "</val_open:1058699154509013067>\n"
                        "</wheel:1058699153842114570>\n\n"
                        "Стоит обратить внимание на команду </bug_report:1058699154257363019>:)"
        )
        self.emb4.set_image(
            url="https://media.discordapp.net/attachments/572705890524725248/1058749306825347132/dpbg1.png"
        )
        if publish == "yes":
            await discord.utils.get(ctx.guild.channels, id=798222242248654888).send(embed=self.emb1)
            await discord.utils.get(ctx.guild.channels, id=798222242248654888).send(embed=self.emb2)
            await discord.utils.get(ctx.guild.channels, id=798222242248654888).send(embed=self.emb3)
            await discord.utils.get(ctx.guild.channels, id=798222242248654888).send(embed=self.emb4)
        else:
            await ctx.send(embed=self.emb1)
            await ctx.send(embed=self.emb2)
            await ctx.send(embed=self.emb3)
            await ctx.send(embed=self.emb4)

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
            logging.error(error)
            try:
                write_log(f"error: {str(ctx.author)} ({ctx.author.id}) "
                          f"({ctx.guild.id})\t {str(error)}\t{str(get_time())}\n")
            except AttributeError:
                pass
