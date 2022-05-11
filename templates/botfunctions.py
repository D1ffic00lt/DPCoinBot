import discord
import math

from ..database.db import Database
from .helperfunction import datetime_to_str, ignore_exceptions, get_time, divide_the_number, logging
from ..version import __version__
from ..config import settings


class BotFunction(Database):
    def __init__(self, filename: str):
        super().__init__(filename)
        self.prises = {}

    @ignore_exceptions
    async def voice_delete_stats(self, member: discord.member, arg: bool) -> None:
        try:
            now2 = self.get_time_from_online_stats(member.id, member.guild.id)
        except TypeError:
            pass
        else:
            time = datetime_to_str(get_time()) - now2
            self.delete_from_online_stats(member.id)
            self.update_minutes_in_voice_channels(int(time.total_seconds() // 60), member.id, member.guild.id)

            if arg is True:
                self.insert_into_online_stats(member.id, member.guild.id)
            minutes = self.get_minutes(member.id, member.guild.id)
            if minutes >= 1 and str(self.get_voice_1_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 500)
                self.set_voice_1_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «Вроде они добрые...»!\nВам начислено 500 коинов!")
            elif minutes >= 10 and str(self.get_voice_10_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 700)
                self.set_voice_10_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «Они добрые!»!\nВам начислено 700 коинов!")
            elif minutes >= 100 and str(self.get_voice_100_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 1500)
                self.set_voice_100_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «Отличная компания»!\nВам начислено 1500 коинов!")
            elif minutes >= 1000 and str(self.get_voice_1000_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 3000)
                self.set_voice_1000_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «А они точно добрые?»!\nВам начислено 3000 коинов!")
            elif minutes >= 10000 and str(self.get_voice_10000_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 7000)
                self.set_voice_10000_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «СПАСИТЕ»!\nВам начислено 7000 коинов!")
            elif minutes >= 100000 and str(self.get_voice_100000_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 14000)
                self.set_voice_100000_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «А может и не надо...»!\nВам начислено 14000 коинов!")
            elif minutes >= 1000000 and str(self.get_voice_1000000_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 28000)
                self.set_voice_1000000_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «Всё-таки они хорошие:)»!\nВам начислено 28000 коинов!")
            elif minutes >= 10000000 and str(self.get_voice_10000000_achievement(member.id, member.guild.id)) == "0":
                self.add_coins(member.id, member.guild.id, 56000)
                self.set_voice_10000000_achievement(member.id, member.guild.id)
                await member.send(f"На сервере {member.guild} "
                                  f"получено достижение «А у меня есть личная жизнь?»!\nВам начислено 56000 коинов!")

    @ignore_exceptions
    async def achievement(self, ctx) -> None:
        loses = self.get_loses_count(ctx.author.id, ctx.guild.id)
        wins = self.get_wins_count(ctx.author.id, ctx.guild.id)
        if self.get_three_losses_in_row_achievement(ctx.author.id, ctx.guild.id) == 0 and loses >= 3:
            self.add_coins(ctx.author.id, ctx.guild.id, 400)
            self.set_three_losses_in_row_achievement(ctx.author.id, ctx.guild.id)
            await ctx.author.send(f"На сервере {ctx.author.guild} "
                                  f"получено достижение «Азартный человек»!\nВам начислено 400 коинов!")

        elif self.get_ten_losses_in_row_achievement(ctx.author.id, ctx.guild.id) == 0 and loses >= 10:
            self.add_coins(ctx.author.id, ctx.guild.id, 3000)
            self.set_ten_losses_in_row_achievement(ctx.author.id, ctx.guild.id)
            await ctx.author.send(f"На сервере {ctx.author.guild} "
                                  f"получено достижение «Сумасшедший»!\nВам начислено 3000 коинов!")

        elif self.get_twenty_losses_in_row_achievement(ctx.author.id, ctx.guild.id) == 0 and loses >= 20:
            self.add_coins(ctx.author.id, ctx.guild.id, 10000)
            self.set_twenty_losses_in_row_achievement(ctx.author.id, ctx.guild.id)
            await ctx.author.send(f"На сервере {ctx.author.guild} "
                                  f"получено достижение «Бессмертный»!\nВам начислено 10000 коинов!")

        elif self.get_three_wins_in_row_achievement(ctx.author.id, ctx.guild.id) == 0 and wins >= 3:
            self.add_coins(ctx.author.id, ctx.guild.id, 400)
            self.set_three_wins_in_row_achievement(ctx.author.id, ctx.guild.id)
            await ctx.author.send(f"На сервере {ctx.author.guild} "
                                  f"получено достижение «Да я богач!»!\nВам начислено 400 коинов!")

        elif self.get_ten_wins_in_row_achievement(ctx.author.id, ctx.guild.id) == 0 and wins >= 10:
            self.add_coins(ctx.author.id, ctx.guild.id, 3000)
            self.set_ten_wins_in_row_achievement(ctx.author.id, ctx.guild.id)
            await ctx.author.send(f"На сервере {ctx.author.guild} "
                                  f"получено достижение «Это вообще законно?»!\nВам начислено 3000 коинов!")

        elif self.get_twenty_wins_in_row_achievement(ctx.author.id, ctx.guild.id) == 0 and wins >= 20:
            self.add_coins(ctx.author.id, ctx.guild.id, 20000)
            self.set_twenty_wins_in_row_achievement(ctx.author.id, ctx.author.id)
            await ctx.author.send(f"На сервере {ctx.author.guild} "
                                  f"получено достижение «Кажется меня не любят...»!\nВам начислено 20000 коинов!")

    @ignore_exceptions
    async def achievement_member(self, member: discord.member) -> None:
        loses = self.get_loses_count(member.id, member.guild.id)
        wins = self.get_wins_count(member.id, member.guild.id)
        if self.get_three_losses_in_row_achievement(member.id, member.guild.id) == 0 and loses >= 3:
            self.add_coins(member.id, member.guild.id, 400)
            self.set_three_losses_in_row_achievement(member.id, member.guild.id)
            await member.send(f"На сервере {member.guild} "
                              f"получено достижение «Азартный человек»!\nВам начислено 400 коинов!")

        elif self.get_ten_losses_in_row_achievement(member.id, member.guild.id) == 0 and loses >= 10:
            self.add_coins(member.id, member.guild.id, 3000)
            self.set_ten_losses_in_row_achievement(member.id, member.guild.id)
            await member.send(f"На сервере {member.guild} "
                              f"получено достижение «Сумасшедший»!\nВам начислено 3000 коинов!")

        elif self.get_twenty_losses_in_row_achievement(member.id, member.guild.id) == 0 and loses >= 20:
            self.add_coins(member.id, member.guild.id, 10000)
            self.set_twenty_losses_in_row_achievement(member.id, member.guild.id)
            await member.send(f"На сервере {member.guild} "
                              f"получено достижение «Бессмертный»!\nВам начислено 10000 коинов!")

        elif self.get_three_wins_in_row_achievement(member.id, member.guild.id) == 0 and wins >= 3:
            self.add_coins(member.id, member.guild.id, 400)
            self.set_three_wins_in_row_achievement(member.id, member.guild.id)
            await member.send(f"На сервере {member.guild} "
                              f"получено достижение «Да я богач!»!\nВам начислено 400 коинов!")

        elif self.get_ten_wins_in_row_achievement(member.id, member.guild.id) == 0 and wins >= 10:
            self.add_coins(member.id, member.guild.id, 3000)
            self.set_ten_wins_in_row_achievement(member.id, member.guild.id)
            await member.send(f"На сервере {member.guild} "
                              f"получено достижение «Это вообще законно?»!\nВам начислено 3000 коинов!")

        elif self.get_twenty_wins_in_row_achievement(member.id, member.guild.id) == 0 and wins >= 20:
            self.add_coins(member.id, member.guild.id, 20000)
            self.set_twenty_wins_in_row_achievement(member.id, member.author.id)
            await member.send(f"На сервере {member.guild} "
                              f"получено достижение «Кажется меня не любят...»!\nВам начислено 20000 коинов!")

    @ignore_exceptions
    async def cash_check(
            self,
            ctx,
            cash: int,
            max_cash: int = None,
            min_cash: int = 1,
            check: bool = False
    ) -> bool:
        if cash is None:
            await ctx.send(f"""{ctx.author.mention}, Вы не ввели сумму!""")
        elif check and cash > self.get_cash(ctx.author.id, ctx.guild.id):
            await ctx.send(f"""{ctx.author.mention}, у Вас недостаточно средств!""")
        else:
            if cash == "all":
                return True
            elif max_cash is not None:
                if (cash < min_cash or cash > max_cash) and ctx.author.id != 401555829620211723:
                    await ctx.send(f'{ctx.author.mention}, нельзя ввести число меньше '
                                   f'{divide_the_number(min_cash)} и больше {divide_the_number(max_cash)}!')
                else:
                    return True
            elif max_cash is None:
                if cash < min_cash and ctx.author.id != 401555829620211723:
                    await ctx.send(f'{ctx.author.mention}, нельзя ввести число меньше {divide_the_number(min_cash)}!')
                else:
                    return True
        return False

    @logging
    @ignore_exceptions
    async def start(self, bot) -> None:
        if not self.checking_for_levels_existence_in_table():
            lvl = 1
            for i in range(1, 405):
                self.insert_into_levels(i, int(math.pow((lvl * 32), 1.4)), i * int(math.pow(lvl, 1.2)))
                lvl += 1
            self.cursor.execute("UPDATE levels SET award = 1500000 WHERE level = 404")
            self.connection.commit()

        self.clear_coinflip()

        await bot.change_presence(status=discord.Status.online, activity=discord.Game(
            f"{settings['prefix']}help"))

        # if not os.path.exists("json_/ban_list.json"):
        #     with open('json_/last_save.json', 'w+') as outfile:
        #         json.dump([], outfile)

        print("Bot connected")
        print("version: {}\n".format(__version__))

    @ignore_exceptions
    async def stats_update(
            self,
            ctx,
            first_arg: str,
            second_arg: str,
            third_arg: str, count
    ) -> None:
        self.update_user_stats1(first_arg, ctx.author.id, ctx.author.id)
        self.update_user_stats2(second_arg, ctx.author.id, ctx.author.id)
        self.update_user_stats3(third_arg, ctx.author.id, ctx.guild.id)
        self.update_user_stats4(count, ctx.author.id, ctx.guild.id)

        if third_arg == "loses":
            self.add_lose(ctx.author.id, ctx.guild.id)
            self.add_win(ctx.author.id, ctx.guild.id, True)

        elif third_arg == "wins":
            self.add_win(ctx.author.id, ctx.guild.id)
            self.add_lose(ctx.author.id, ctx.guild.id, True)

        await self.achievement(ctx)

    # async def voice_delete(self, member, arg: bool, stream: bool = False):
    #     try:
    #         now2 = self.get_time_from_online_stats(member.id, member.guild.id)
    #     except TypeError:
    #         pass
    #     else:
    #         lvl = self.get_level(member.id, member.guild.id)
    #         if lvl != 1:
    #             if lvl != 5:
    #                 lvl *= 2
    #             else:
    #                 lvl *= 4
    #         minutes = self.get_minutes(member.id, member.guild.id)
    #         self.add_coins(member.id, member.guild.id, minutes * (datetime_to_str(get_time()) - now2))
    #         cursor.execute(
    #             "DELETE FROM online WHERE id = {}".format(member.id))
    #         connection.commit()
    #         cursor.execute(
    #             "UPDATE users SET voice_minutes = voice_minutes + ? WHERE id = ? AND server_id = ?",
    #             [mint, member.id, member.guild.id])
    #
    #         connection.commit()
    #
    #         month = int(datetime.today().strftime('%m'))
    #         day = int(datetime.today().strftime('%d'))
    #         if month > 11 or month == 1:
    #             if (month == 12 and day > 10) or (month == 1 and day < 15):
    #                 prises[member.id] = 0
    #                 for i in range(mint):
    #                     if random.randint(1, 3) == 3:
    #                         if random.randint(1, 3) == 3:
    #                             if random.randint(1, 3) == 3:
    #                                 if random.randint(1, 3) == 1:
    #                                     if random.randint(1, 3) == 3:
    #                                         prises[member.id] += 1
    #                 if prises[member.id] != 0:
    #                     cursor.execute(
    #                         "UPDATE inventory SET new_year_prises = new_year_prises"
    #                         " + ? WHERE id = ? AND server_id = ?", [prises[member.id], member.id, member.guild.id])
    #                     try:
    #                         await member.send(
    #                             "Вам начислено {} новогодних подарков! Чтобы открыть их пропишите //open\n"
    #                             "У нас кстати новогодний ивент:) пиши //help new_year".format(
    #                                 prises[member.id]))
    #                     except discord.errors.Forbidden:
    #                         pass
    #         if month == 2 and day == 14:
    #             valentine[member.id] = 0
    #             for i in range(mint):
    #                 if random.randint(0, 4) == 1:
    #                     if random.randint(0, 4) == 2:
    #                         if random.randint(0, 4) == 3:
    #                             valentine[member.id] += 1
    #             if valentine[member.id] != 0:
    #                 cursor.execute(
    #                     "UPDATE inventory SET valentine = valentine"
    #                     " + ? WHERE id = ? AND server_id = ?", [valentine[member.id], member.id, member.guild.id])
    #                 try:
    #                     await member.send(
    #                         "Вам пришло {} валентинок! Чтобы открыть их пропишите //val_open".format(
    #                             valentine[member.id]))
    #                 except discord.errors.Forbidden:
    #                     pass
    #         if arg is True:
    #             if stream:
    #                 cursor.execute(
    #                     "INSERT INTO online VALUES (?, ?, ?, 1)", [member.id, member.guild.id, str(get_time())])
    #             elif stream is False:
    #                 cursor.execute(
    #                     "INSERT INTO online VALUES (?, ?, ?, 0)", [member.id, member.guild.id, str(get_time())])
    #             connection.commit()
