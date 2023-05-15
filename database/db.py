# -*- coding: utf-8 -*-
import smtplib
import numpy as np
import sqlalchemy.ext.declarative as dec

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union
from discord.ext import commands
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DEBUG_EMAIL, PASSWORD
from units.additions import *
from units.encoding import Encoder
from . import __all_models


class Database(object):
    def __init__(self, filename: str, encoder: Encoder) -> None:
        self.encoder: Encoder = encoder
        self.check_str_cash = lambda cash, user_cash: int(cash) > user_cash if str(cash).isdigit() else False
        self.filename: str = filename

    # async def voice_delete_stats(self, member: discord.Member, arg: bool = True) -> None:
    #     try:
    #         now2 = self.get_time_from_online_stats(member.id, member.guild.id)
    #     except TypeError:
    #         pass
    #     else:
    #         time = int((datetime_to_str(get_time()) - now2).total_seconds() // 60)
    #         self.delete_from_online_stats(member.id)
    #         self.update_minutes_in_voice_channels(time, member.id, member.guild.id)
    #
    #         if arg is True:
    #             self.insert_into_online_stats(member.id, member.guild.id)
    #         minutes = self.get_minutes(member.id, member.guild.id)
    #         if minutes >= 1 and str(self.get_voice_1_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 500)
    #             self.set_voice_1_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «Вроде они добрые...»!\nВам начислено 500 коинов!"
    #             )
    #         elif minutes >= 10 and str(self.get_voice_10_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 700)
    #             self.set_voice_10_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «Они добрые!»!\nВам начислено 700 коинов!"
    #             )
    #         elif minutes >= 100 and str(self.get_voice_100_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 1500)
    #             self.set_voice_100_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «Отличная компания»!\nВам начислено 1500 коинов!"
    #             )
    #         elif minutes >= 1000 and str(self.get_voice_1000_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 3000)
    #             self.set_voice_1000_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «А они точно добрые?»!\nВам начислено 3000 коинов!"
    #             )
    #         elif minutes >= 10000 and str(self.get_voice_10000_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 7000)
    #             self.set_voice_10000_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «СПАСИТЕ»!\nВам начислено 7000 коинов!"
    #             )
    #         elif minutes >= 100000 and str(self.get_voice_100000_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 14000)
    #             self.set_voice_100000_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «А может и не надо...»!\nВам начислено 14000 коинов!"
    #             )
    #         elif minutes >= 1000000 and str(self.get_voice_1000000_achievement(member.id, member.guild.id)) == "0":
    #             self.add_coins(member.id, member.guild.id, 28000)
    #             self.set_voice_1000000_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «Всё-таки они хорошие:)»!\nВам начислено 28000 коинов!"
    #             )
    #         elif minutes >= 10000000 and str(
    #                 self.get_voice_10000000_achievement(member.id, member.guild.id)
    #         ) == "0":
    #             self.add_coins(member.id, member.guild.id, 56000)
    #             self.set_voice_10000000_achievement(member.id, member.guild.id)
    #             await member.send(
    #                 f"На сервере {member.guild} "
    #                 f"получено достижение «А у меня есть личная жизнь?»!\nВам начислено 56000 коинов!"
    #             )
    #
    # async def achievement(self, ctx: Union[commands.context.Context, discord.Interaction]) -> None:
    #     if isinstance(ctx, discord.Interaction):
    #         author_id = ctx.user.id
    #     else:
    #         author_id = ctx.author.id
    #     loses = self.get_loses_count(author_id, ctx.guild.id)
    #     wins = self.get_wins_count(author_id, ctx.guild.id)
    #     if self.get_three_losses_in_row_achievement(author_id, ctx.guild.id) == 0 and loses >= 3:
    #         self.add_coins(author_id, ctx.guild.id, 400)
    #         self.set_three_losses_in_row_achievement(author_id, ctx.guild.id)
    #         await ctx.author.send(
    #             f"На сервере {ctx.author.guild} "
    #             f"получено достижение «Азартный человек»!\nВам начислено 400 коинов!"
    #         )
    #
    #     elif self.get_ten_losses_in_row_achievement(author_id, ctx.guild.id) == 0 and loses >= 10:
    #         self.add_coins(author_id, ctx.guild.id, 3000)
    #         self.set_ten_losses_in_row_achievement(author_id, ctx.guild.id)
    #         await ctx.author.send(
    #             f"На сервере {ctx.author.guild} "
    #             f"получено достижение «Сумасшедший»!\nВам начислено 3000 коинов!"
    #         )
    #
    #     elif self.get_twenty_losses_in_row_achievement(author_id, ctx.guild.id) == 0 and loses >= 20:
    #         self.add_coins(author_id, ctx.guild.id, 10000)
    #         self.set_twenty_losses_in_row_achievement(author_id, ctx.guild.id)
    #         await ctx.author.send(
    #             f"На сервере {ctx.author.guild} "
    #             f"получено достижение «Бессмертный»!\nВам начислено 10000 коинов!"
    #         )
    #
    #     elif self.get_three_wins_in_row_achievement(author_id, ctx.guild.id) == 0 and wins >= 3:
    #         self.add_coins(author_id, ctx.guild.id, 400)
    #         self.set_three_wins_in_row_achievement(author_id, ctx.guild.id)
    #         await ctx.author.send(
    #             f"На сервере {ctx.author.guild} "
    #             f"получено достижение «Да я богач!»!\nВам начислено 400 коинов!"
    #         )
    #
    #     elif self.get_ten_wins_in_row_achievement(author_id, ctx.guild.id) == 0 and wins >= 10:
    #         self.add_coins(author_id, ctx.guild.id, 3000)
    #         self.set_ten_wins_in_row_achievement(author_id, ctx.guild.id)
    #         await ctx.author.send(
    #             f"На сервере {ctx.author.guild} "
    #             f"получено достижение «Это вообще законно?»!\nВам начислено 3000 коинов!"
    #         )
    #
    #     elif self.get_twenty_wins_in_row_achievement(author_id, ctx.guild.id) == 0 and wins >= 20:
    #         self.add_coins(author_id, ctx.guild.id, 20000)
    #         self.set_twenty_wins_in_row_achievement(author_id, author_id)
    #         await ctx.author.send(
    #             f"На сервере {ctx.author.guild} "
    #             f"получено достижение «Кажется меня не любят...»!\nВам начислено 20000 коинов!"
    #         )
    #
    # async def achievement_member(self, member: discord.Member) -> None:
    #     loses = self.get_loses_count(member.id, member.guild.id)
    #     wins = self.get_wins_count(member.id, member.guild.id)
    #     if self.get_three_losses_in_row_achievement(member.id, member.guild.id) == 0 and loses >= 3:
    #         self.add_coins(member.id, member.guild.id, 400)
    #         self.set_three_losses_in_row_achievement(member.id, member.guild.id)
    #         await member.send(
    #             f"На сервере {member.guild} "
    #             f"получено достижение «Азартный человек»!\nВам начислено 400 коинов!"
    #         )
    #
    #     elif self.get_ten_losses_in_row_achievement(member.id, member.guild.id) == 0 and loses >= 10:
    #         self.add_coins(member.id, member.guild.id, 3000)
    #         self.set_ten_losses_in_row_achievement(member.id, member.guild.id)
    #         await member.send(
    #             f"На сервере {member.guild} "
    #             f"получено достижение «Сумасшедший»!\nВам начислено 3000 коинов!"
    #         )
    #
    #     elif self.get_twenty_losses_in_row_achievement(member.id, member.guild.id) == 0 and loses >= 20:
    #         self.add_coins(member.id, member.guild.id, 10000)
    #         self.set_twenty_losses_in_row_achievement(member.id, member.guild.id)
    #         await member.send(
    #             f"На сервере {member.guild} "
    #             f"получено достижение «Бессмертный»!\nВам начислено 10000 коинов!"
    #         )
    #
    # async def cash_check(
    #         self, ctx: Union[commands.context.Context, discord.Interaction],
    #         cash: Union[str, int], max_cash: int = None,
    #         min_cash: int = 1, check: bool = False
    # ) -> bool:
    #     mention = ctx.author.mention if isinstance(ctx, commands.context.Context) else ctx.user.mention
    #     author_id = ctx.author.id if isinstance(ctx, commands.context.Context) else ctx.user.id
    #     if cash is None:
    #         message = f"{mention}, Вы не ввели сумму!"
    #         if isinstance(ctx, commands.context.Context):
    #             await ctx.send(message)
    #         else:
    #             await ctx.response.send_message(message, ephemeral=True)
    #     elif check and self.check_str_cash(cash, self.get_cash(author_id, ctx.guild.id)):
    #         message = f"{mention}, у Вас недостаточно средств!"
    #         if isinstance(ctx, commands.context.Context):
    #             await ctx.send(message)
    #         else:
    #             await ctx.response.send_message(message, ephemeral=True)
    #     else:
    #         if cash == "all":
    #             return True
    #         elif max_cash is not None:
    #             if (int(cash) < min_cash or int(cash) > max_cash) and author_id != 401555829620211723:
    #                 message = f'{mention}, нельзя ввести число меньше ' \
    #                                f'{divide_the_number(min_cash)} и больше {divide_the_number(max_cash)}!'
    #                 if isinstance(ctx, commands.context.Context):
    #                     await ctx.send(message)
    #                 else:
    #                     await ctx.response.send_message(message, ephemeral=True)
    #             else:
    #                 return True
    #         elif max_cash is None:
    #             if int(cash) < min_cash and ctx.author.id != 401555829620211723:
    #                 message = f'{mention}, нельзя ввести число меньше {divide_the_number(min_cash)}!'
    #                 if isinstance(ctx, commands.context.Context):
    #                     await ctx.send(message)
    #                 else:
    #                     await ctx.response.send_message(message, ephemeral=True)
    #             else:
    #                 return True
    #     return False
    #
    # async def stats_update(
    #         self, ctx: Union[commands.context.Context, discord.Interaction],
    #         first_arg: str, second_arg: str,
    #         third_arg: str, count: int
    # ) -> None:
    #     if isinstance(ctx, discord.Interaction):
    #         author_id = ctx.user.id
    #     else:
    #         author_id = ctx.author.id
    #     self.update_user_stats_1(first_arg, author_id, ctx.guild.id)
    #     self.update_user_stats_2(second_arg, third_arg, author_id, ctx.guild.id)
    #     self.update_user_stats_3(third_arg, author_id, ctx.guild.id)
    #     self.update_user_stats_4(count, author_id, ctx.guild.id)
    #
    #     if third_arg == "LosesCount":
    #         self.add_lose(author_id, ctx.guild.id)
    #         self.add_win(author_id, ctx.guild.id, True)
    #
    #     elif third_arg == "WinsCount":
    #         self.add_win(author_id, ctx.guild.id)
    #         self.add_lose(author_id, ctx.guild.id, True)
    #
    #     await self.achievement(ctx)
    #
    # async def voice_delete(self, member: discord.Member, arg: bool = True) -> None:
    #     try:
    #         now2 = self.get_time_from_online_stats(member.id, member.guild.id)
    #     except TypeError:
    #         pass
    #     else:
    #         minutes = int((datetime_to_str(get_time()) - now2).total_seconds() // 60)
    #         self.add_coins(member.id, member.guild.id, minutes)
    #         self.delete_from_online(member.id)
    #         self.update_minutes_in_voice_channels(minutes, member.id, member.guild.id)
    #         month = int(datetime.today().strftime('%m'))
    #         day = int(datetime.today().strftime('%d'))
    #         if month > 11 or month == 1:
    #             if (month == 12 and day > 10) or (month == 1 and day < 15):
    #                 self.prises[member.id] = 0
    #                 for i in range(minutes):
    #                     if len(set(np.random.randint(1, 6, 5))) == 3 and len(set(np.random.randint(1, 6, 5))) == 3:
    #                         self.prises[member.id] += 1
    #                 if self.prises[member.id] != 0:
    #                     self.add_present(self.prises[member.id], member.id, member.guild.id)
    #                     try:
    #                         await member.send(
    #                             "Вам начислено {} новогодних подарков! Чтобы открыть их пропишите //open\n"
    #                             "У нас кстати новогодний ивент:) пиши //help new_year".format(
    #                                 self.prises[member.id]
    #                             )
    #                         )
    #                     except discord.errors.Forbidden:
    #                         pass
    #         if month == 2 and day == 14:
    #             self.valentine[member.id] = 0
    #             for i in range(minutes):
    #                 if len(set(np.random.randint(1, 6, 5))) == 3 and len(set(np.random.randint(1, 6, 5))) == 3:
    #                     self.valentine[member.id] += 1
    #             if self.valentine[member.id] != 0:
    #                 self.add_valentines(self.valentine[member.id], member.id, member.guild.id)
    #                 try:
    #                     await member.send(
    #                         "Вам пришло {} валентинок! Чтобы открыть их пропишите //val_open".format(
    #                             self.valentine[member.id]
    #                         )
    #                     )
    #                 except discord.errors.Forbidden:
    #                     pass
    #         if arg:
    #             self.insert_into_stats(member.id, member.guild.id)
    #
    # def is_the_casino_allowed(self, channel_id: int) -> bool:
    #     if self.cursor.execute(
    #             "SELECT `CasinoChannelID` FROM `Server` WHERE `GuildID` = ?",
    #             (channel_id,)
    #     ).fetchone() is None:
    #         return True
    #     if channel_id in [572705890524725248, 573712070864797706] or \
    #             self.cursor.execute(
    #                 "SELECT `CasinoChannelID` FROM `Server` WHERE `GuildID` = ?",
    #                 (channel_id,)
    #             ).fetchone():
    #         return True
    #     return False
    #
    # def send_files(self):
    #     server = smtplib.SMTP('smtp.gmail.com: 587')
    #     msg = MIMEMultipart()
    #     part2 = MIMEBase('application', "octet-stream")
    #     part1 = MIMEBase('application', "octet-stream")
    #
    #     part1.set_payload(open(self.filename, "rb").read())
    #     part2.set_payload(open(".logs/develop_logs.dpcb", "rb").read())
    #
    #     encoders.encode_base64(part1)
    #     encoders.encode_base64(part2)
    #
    #     part1.add_header(
    #         'Content-Disposition', "attachment; filename= %s" % os.path.basename(self.filename)
    #     )
    #     part2.add_header(
    #         'Content-Disposition', "attachment; filename= %s" % os.path.basename(".logs/develop_logs.dpcb")
    #     )
    #
    #     msg['From'] = self.encoder.decrypt(DEBUG_EMAIL)
    #     msg['To'] = self.encoder.decrypt(DEBUG_EMAIL)
    #     msg['Subject'] = "Копии"
    #
    #     msg.attach(part1)
    #     msg.attach(part2)
    #
    #     msg.attach(MIMEText("Копии от {}".format(str(get_time()))))
    #     server.starttls()
    #     server.login(msg['From'], self.encoder.decrypt(PASSWORD))
    #     server.sendmail(msg['From'], msg['To'], msg.as_string())
    #     server.quit()
    #     write_log("[{}] [INFO]: Копии данных отправлена на почту".format(str(get_time())))
