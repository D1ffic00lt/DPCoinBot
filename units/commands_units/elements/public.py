# -*- coding: utf-8 -*-
import logging
import discord

from discord.ext import commands
from datetime import datetime

from config import PREFIX
from units.texts import *

__all__ = (
    "Public",
)


class Public(commands.Cog):
    NAME = 'public module'

    __slots__ = (
        "db", "bot", "row12",
        "row22", "row32", "month", "day"
    )

    def __init__(self, bot: commands.Bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot: commands.Bot = bot
        logging.info(f"Public connected")

    @commands.command(aliases=["info"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __info(self, ctx: commands.context.Context):
        emb = discord.Embed(title="За что выдают коины?")
        emb.add_field(
            name='Общение в голосовых каналах',
            value='Бот начисляет 1 коин за 1 минуту нахождения в голосовом канале(коины начисляются после '
                  'выхода из канала)'
        )
        emb.add_field(
            name='Общение в чате',
            value='С шансом 1 к 3 бот начисляет 1 коин за одно НЕ ПОВТОРЯЮЩЕЕ ПРОШЛОЕ сообщение в чате, '
                  'не менее 7 символов'
        )
        emb.add_field(
            name='Администрация',
            value='Администрация может выдавать коины'
        )
        await ctx.reply(embed=emb)

    @commands.command(aliases=["help"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __help(self, ctx: commands.context.Context, arg: str = None):
        if arg == "admin":
            emb = discord.Embed(title="Команды бота:")
            emb.add_field(name="```НАСТРОЙКА СЕРВЕРА```", value=setup_value)
            emb.add_field(
                name=f'{PREFIX}auto_setup',
                value='Авто настройка бота, бот создаст категорию, 2 текстовых канала(для казино'
                      ' и для выдачи товаров) и роль, которая сможет выдавать коины, далее бот выдаст инструкции по'
                      ' дальнейшей настройки\n'
                      '```diff\n'
                      '- ЕСЛИ КОГДА-ЛИБО У ВАС УЖЕ БЫЛ ПРОПИСАН setup,'
                      'ТО БОТ УДАЛИТ РОЛЬ И КАНАЛЫ, КОТОРЫЕ БЫЛИ СОЗДАНЫ'
                      '```',
                inline=False)
            emb.add_field(
                name=f'{PREFIX}setup <Упоминание роли> <Упоминание канала для отправки покупок> '
                     f'<Упоминание канал для казино>',
                value='Настроить бота, Роль, которая сможет выдавать коины, канал, в который будут отправляться '
                      'заказы через buye, канал, в котором доступно казино',
                inline=False)
            emb.add_field(name=f'**{PREFIX}give <Упоминание пользователя> <Сумма>**',
                               value='Выдать деньги пользователю', inline=False)
            emb.add_field(name=f'**{PREFIX}take <Упоминание пользователя> <Сумма(Либо all для '
                                    f'обнуления '
                                    f'счёта)>**',
                               value='Забрать деньги у пользователя', inline=False)
            emb.add_field(name=f'**{PREFIX}give-role <Упоминание роли> <Сумма>**',
                               value='Выдать деньги пользователю', inline=False)
            emb.add_field(name=f'**{PREFIX}take-role <Упоминание роли> <Сумма(Либо all для '
                                    f'обнуления '
                                    f'счёта)>**',
                               value='Забрать деньги у пользователя', inline=False)
            emb.add_field(name=f'**{PREFIX}add-shop <Упоминание роли> <Цена>**',
                               value='Добавить роль в магазин', inline=False)
            emb.add_field(name=f'**{PREFIX}start_money**',
                               value='Стартовый баланс при входе на сервер', inline=False)
            emb.add_field(name=f'**{PREFIX}start_money set <Количество>**',
                               value='Установить стартовый баланс при входе на сервер', inline=False)
            emb.add_field(name=f'**{PREFIX}del_games <Упоминание пользователя>**',
                               value='Удалить все активные игры для определённого пользователя', inline=False)
            emb.add_field(name=f'**{PREFIX}add-else <Цена> <То, что вы хотите добавить в '
                                    f'магазин>**',
                               value='Добавить какой-либо предмет в магазин'
                                     '(примечание: после добавление предмету будет '
                                     'выдан id, buye **1** - id выделен',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}remove-else <id>**',
                               value='Удалить какой-либо предмет из магазина', inline=False)
            emb.add_field(name=f'**{PREFIX}remove-shop <Упоминание роли>**',
                               value='Удалить роль из магазина', inline=False)
            await ctx.reply(embed=emb)
        elif arg == "casino":
            row12 = "3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36"
            row22 = "2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35"
            row32 = "1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34"
            emb = discord.Embed(title="Команды бота:")
            emb.add_field(name=f'Как работает rust casino?',
                               value='Если простым языком, то Вы ставите какую-либо сумму '
                                     '(эта сумма с Вас снимается) на '
                                     'число ( '
                                     'либо 1, либо 3, либо 5, либо 10, либо 20), если выпадает число 1, то ставка '
                                     'умножается в '
                                     '2 раза, если 3, то в 3 раза, если 5, то в 5 раз и тд, '
                                     'чем меньше число - тем больше шанс на выигрыш', inline=False)
            emb.add_field(name=f'А если сложным языком?',
                               value='Ну а если вы хотите поломать себе мозги, '
                                     'то вот как работает это казино: существует '
                                     'массив из чисел 1, 3, 5, 10, 20, '
                                     'когда Вы прописываете эту команду, массив '
                                     'перемешивается, и число, у которого будет '
                                     'индекс 0 - будет выигрышным, казино построено '
                                     'на модуле random, и повлиять на него '
                                     'без '
                                     'доступа к коду практические невозможно, '
                                     'но даже если у вас есть доступ к коду, быстро '
                                     'сделать это не получится никак, это для '
                                     'тех, кто говорит, что подкрут))', inline=False)
            emb.add_field(name=f'Как работает coinflip с ботом?',
                               value=f"Ну тут всё проще. Вы прописываете {PREFIX}coinflip <сумма>"
                                     f"дальше программа выбирает n число(1 или 2), "
                                     f"если выпадает 1 - побеждаете Вы, и сумма, "
                                     f"которую Вы поставили, умножается в 2 раза, если выпадает 2 - вы проигрываете",
                               inline=False)
            emb.add_field(name=f'Как работает coinflip с другим человеком?',
                               value=f"Тут всё немного сложнее. Вы прописываете {PREFIX}coinflip <сумма> "
                                     f"<упоминание второго игрока>, а второй игрок прописывает "
                                     f"{PREFIX}accept <упоминание первого игрока(Вас)>. "
                                     f"После этого программа также выбирает 2 числа, "
                                     f"если выпадает 1, то побеждаете Вы, "
                                     f"если 2, то Ваш противник", inline=False)
            emb.add_field(name=f'Команды коинфлипа на двух игроков',
                               value=f"**{PREFIX}coinflip <сумма> "
                                     f"<упоминание второго игрока>** - старт коинфлипа\n"
                                     f"**{PREFIX}accept <упоминание игрока>** - принять коинфлип\n"
                                     f"**{PREFIX}reject <упоминание игрока>** - отклонить коинфлип\n"
                                     f"**{PREFIX}games** - все Ваши активные игры\n"
                                     f"**{PREFIX}del_games** - отклонить все активные игры", inline=False)
            emb.add_field(name=f"Как работает казино 777?",
                               value=f"Вы ставите ставку, программа генерирует 3 ряда чисел\n"
                                     f"**Случаи выигрыша:**\n"
                                     f"Строка с +, три одинаковых числа в ряд\n"
                                     f"Три одинаковых числа по диагонали\n"
                                     f"**Во сколько раз умножается выигрыш?**\n"
                                     f"Три восьмёрки - в 2 раза\n"
                                     f"Три нуля - в 3 раза\n"
                                     f"Три семёрки - в 5 раз\n"
                                     f"Три единицы - вы ничего не теряете, но и ничего не получаете", inline=False)
            emb.add_field(name=f"Как работает roll?",
                               value="**{}roll <Ставка> <Число или аргумент>**\n"
                                     "Вы можете поставить определённую сумму на "
                                     "числа(от 0 до 36), цвета, и наборы чисел.\n"
                                     'Аргументы:\n'
                                     '**Число** - поставить на число\n'
                                     '**1st12** - число от 1 до 12\n'
                                     '**2nd12** - число от 12 до 24\n'
                                     '**3rd12** - число от 24 до 26\n'
                                     '**1to18** - число от 1 до 18\n'
                                     '**19to36** - число от 19 до 36\n'
                                     '**2to1** - числа {}\n'
                                     '**2to2** - числа {}\n'
                                     '**2to3** - числа {}\n'
                                     '**r** - поставить на красный цвет\n'
                                     '**b** - поставить на чёрный цвет\n'
                                     '**ch** - поставить на чётное\n'
                                     '**nch** - поставить на нечётное\n'
                                     "**Во сколько раз умножается выигрыш?**\n"
                                     "1st12/2nd12/3rd/12 - в **3 раза**\n"
                                     "1to18/19to36 - в **2 раза**\n"
                                     "2to1/2to2/2to3 - **в 3 раза**\n"
                                     "ch/nch - **в 2 раза**\n"
                                     "Число - **в 35 раз**\n".format(
                                            PREFIX, row12, row22, row32
                                        )
                               )
            emb.add_field(name=f"Как работает fail?",
                               value=f"Вы ставите на определённый коэффициент, "
                                     f"если программа выдаёт коэффициент выше Вашего"
                                     f" - Вы выиграли, и Ваша ставка умножается на Ваш коэффициент", inline=False)
            await ctx.reply(embed=emb)
        elif arg == "me_pls:(":
            if ctx.author.id == 401555829620211723:
                await ctx.reply(
                    "//send_logs - отправить логи\n//send_base - отправить бд\n//logs <Кол-во "
                    "строк>\n//debug <Кол-во строк> "
                    "- отправить логи отладки\n"
                    "//send_webhook <Параметр> - отправить обновление(push), ничего - тест"
                    "//bot_stats - статистика бота\n"
                    "//card_add <id> <Параметр> - добавить параметр в карточку\n"
                    "//card_remove <id> <Параметр> - удалить параметр из карточки\n"
                    "**параметры:** gg - зелёная галочка, "
                    "bg - синяя галочка, dv - разработчик, cd - программист\n\n"
                    "//add_to_ban_list <server_id> - добавить сервер в банлист\n"
                    f"{PREFIX}develop_stats <Параметр (lb, slb)> <Параметр (on, off)> - ну тут понятно"
                )
        elif arg == "new_year":
            emb = discord.Embed(title="Команды Нового года")
            emb.add_field(name=f'**{PREFIX}presents**',
                               value='Все ваши подарки', inline=False)
            emb.add_field(name=f'**{PREFIX}present <упоминание игрока> <количество>**',
                               value='Подарить кому-то подарок', inline=False)
            emb.add_field(name=f'**{PREFIX}open <Аргумент>**',
                               value='Открыть подарок\nАргументы: all - открыть все подарки, '
                                     'число - определённое количество',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}foodshop**',
                               value='Магазин еды', inline=False)
            emb.add_field(name=f'**{PREFIX}food**',
                               value='Ваша еда', inline=False)
            emb.add_field(name=f'**{PREFIX}use <Номер из foodshop>**',
                               value='Использовать еду', inline=False)
            emb.add_field(name=f'**{PREFIX}buyfood <Номер из foodshop> <Количество>**',
                               value='Купить еду', inline=False)
            await ctx.reply(embed=emb)

        elif arg == "tests":
            if ctx.author.id == 401555829620211723 or ctx.author.id == 608314233079201834:
                row12 = "3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36"
                row22 = "2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35"
                row32 = "1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34"

                emb = discord.Embed(title="Команды бета тестеров:")
                emb.add_field(name=f'**{PREFIX}roll <Ставка> <Цифра или аргумент>**',
                                   value='Аргументы:\n'
                                         '1st12 - число от 1 до 12\n'
                                         '2nd12 - число от 12 до 24\n'
                                         '3rd12 - число от 24 до 26\n'
                                         '1to18 - число от 1 до 18\n'
                                         '19to36 - число от 19 до 36\n'
                                         '2to1 - числа {}\n'
                                         '2to2 - числа {}\n'
                                         '2to3 - числа {}\n'
                                         'w - поставить на белый цвет\n'
                                         'b - поставить на чёрный цвет\n'
                                         'ch - поставить на чётное\n'
                                         'nch - поставить на нечётное\n'.format(
                                               row12, row22, row32
                                           ), inline=False)
                await ctx.reply(embed=emb)

        elif arg is None:
            emb = discord.Embed(title="Команды бота:")
            emb.add_field(name=f'**{PREFIX}info**',
                               value='За что выдают коины', inline=False)
            emb.add_field(name=f'**{PREFIX}cash <Упоминание пользователя>**',
                               value='Узнать баланс', inline=False)
            emb.add_field(name=f'**{PREFIX}send <Упоминание пользователя> <Сумма>**',
                               value='Перевести деньги', inline=False)
            emb.add_field(name=f'**{PREFIX}shop**',
                               value='Открыть магазин', inline=False)
            emb.add_field(name=f'**{PREFIX}buy <Упоминание роли>**',
                               value='Купить роль', inline=False)
            emb.add_field(name=f'**{PREFIX}rust_casino <Ставка> <Число(1, 3, 5, 10, 20)>**',
                               value=f'Казино, для подробной информации **{PREFIX}help casino**',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}fail <Ставка> <Коэффициент>**',
                               value=f'Fail, для подробной информации **{PREFIX}help casino**',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}777 <Ставка>**',
                               value=f'Казино 777, для подобной информации **{PREFIX}help casino**',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}roll <Ставка> <Аргумент>**',
                               value=f'Рулетка, для подобной информации **{PREFIX}help casino**',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}stats <Упоминание пользователя>**',
                               value=f'Посмотреть статистику',
                               inline=False)
            emb.add_field(name=f'**{PREFIX}buye <Номер товара>**',
                               value='Купить другой товар сервера', inline=False)
            emb.add_field(name=f'**{PREFIX}bank**',
                               value='Узнать баланс на счету', inline=False)
            emb.add_field(name=f'**{PREFIX}bank add <Сумма>**',
                               value='Положить деньги на счёт', inline=False)
            emb.add_field(name=f'**{PREFIX}bank take <Сумма>**',
                               value='Снять деньги со счёта', inline=False)
            emb.add_field(name=f'**{PREFIX}levels**',
                               value='Информация о левелах', inline=False)
            emb.add_field(name=f'**{PREFIX}lvl_up**',
                               value='Поднять себе левл', inline=False)
            emb.add_field(name=f'**{PREFIX}lb**',
                               value='Рейтинг богачей сервера', inline=False)
            emb.add_field(name=f'**{PREFIX}lb chat**',
                               value='Рейтинг чата сервера', inline=False)
            emb.add_field(name=f'**{PREFIX}lb voice**',
                               value='Рейтинг голосовых каналов сервера', inline=False)
            emb.add_field(name=f'**{PREFIX}slb**',
                               value='Общий баланс сервера', inline=False)
            emb.add_field(name=f'**{PREFIX}del_games**',
                               value='Удалить все активные игры', inline=False)
            emb.add_field(name=f'**{PREFIX}promo <Промокод>**',
                               value='Активировать промокод', inline=False)
            emb.add_field(name=f'**{PREFIX}promo_create <Сумма>**',
                               value='Создать промокод', inline=False)
            emb.add_field(name=f'**{PREFIX}promocodes <Промокод>**',
                               value='Все Ваши промокоды(писать в личные сообщения)', inline=False)
            emb.add_field(name=f'**{PREFIX}card**',
                               value='Получить вашу карточку', inline=False)
            month = int(datetime.today().strftime('%m'))
            day = int(datetime.today().strftime('%d'))
            if month == 2 and day == 14:
                emb.add_field(name=f'**{PREFIX}val_open <аргумент>**',
                                   value='Открыть валентинки\n'
                                         'Аргументы: all - открыть все валентинки, число - определённое количество',
                                   inline=False)
            emb.add_field(name='Помощь для администрации',
                               value=f'**{PREFIX}help admin** - помощь для администрации', inline=False)
            await ctx.reply(embed=emb)
        else:
            emb = discord.Embed(title="Команды бота:")
            emb.add_field(name='Ошибка',
                               value=f'Аргумент неверен!', inline=False)
            await ctx.reply(embed=emb)
