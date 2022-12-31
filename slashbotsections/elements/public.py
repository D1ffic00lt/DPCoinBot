import discord
from discord import app_commands

from discord.ext import commands
from datetime import datetime

from botsections.functions.additions import get_time, write_log
from botsections.functions.config import settings
from botsections.functions.texts import *
from database.db import Database

__all__ = (
    "PublicSlash",
)


class PublicSlash(commands.Cog):
    NAME = 'public module'

    __slots__ = (
        "db", "bot", "row12",
        "row22", "row32", "month", "day"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.bot: commands.Bot = bot
        self.emb: discord.Embed
        self.row12: str
        self.row22: str
        self.row32: str
        self.month: int = 0
        self.day: int = 0
        print(f"[{get_time()}] [INFO]: Public connected")
        write_log(f"[{get_time()}] [INFO]: Public connected")

    @app_commands.command(name="info", description="За что выдают коины?")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def __info(self, inter: discord.Interaction):
        self.emb = discord.Embed(title="За что выдают коины?")
        self.emb.add_field(
            name='Общение в голосовых каналах',
            value='Бот начисляет 1 коин за 1 минуту нахождения в голосовом канале(коины начисляются после '
                  'выхода из канала)'
        )
        self.emb.add_field(
            name='Общение в чате',
            value='С шансом 1 к 3 бот начисляет 1 коин за одно НЕ ПОВТОРЯЮЩЕЕ ПРОШЛОЕ сообщение в чате, '
                  'не менее 7 символов'
        )
        self.emb.add_field(
            name='Администрация',
            value='Администрация может выдавать коины'
        )
        await inter.response.send_message(embed=self.emb)

    @app_commands.command(name="help", description="Информация о командах бота")
    @app_commands.choices(arg=[
        app_commands.Choice(name="Пользователь", value="user"),
        app_commands.Choice(name="Казино", value="casino"),
        app_commands.Choice(name="Новый Год", value="new_year"),
        app_commands.Choice(name="Администратор", value="admin")
    ])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def __help(self, inter: discord.Interaction, arg: app_commands.Choice[str]):
        if arg.value == "admin":
            if inter.user.guild_permissions.administrator or inter.user.id == 401555829620211723:
                self.emb = discord.Embed(title="Команды бота:")
                self.db.get_administrator_role_id(inter.guild.id)
                if isinstance(self.db.get_administrator_role_id(inter.guild.id), bool):
                    self.emb.add_field(name="```НАСТРОЙКА СЕРВЕРА```", value=setup_value)
                self.emb.add_field(
                    name=f'{settings["prefix"]}auto_setup',
                    value='Авто настройка бота, бот создаст категорию, 2 текстовых канала(для казино'
                          ' и для выдачи товаров) и роль, которая сможет выдавать коины, далее бот выдаст инструкции по'
                          ' дальнейшей настройки\n'
                          '```diff\n'
                          '- ЕСЛИ КОГДА-ЛИБО У ВАС УЖЕ БЫЛ ПРОПИСАН setup,'
                          'ТО БОТ УДАЛИТ РОЛЬ И КАНАЛЫ, КОТОРЫЕ БЫЛИ СОЗДАНЫ'
                          '```',
                    inline=False)
                self.emb.add_field(
                    name=f'{settings["prefix"]}setup <Упоминание роли> <Упоминание канала для отправки покупок> '
                         f'<Упоминание канал для казино>',
                    value='Настроить бота, Роль, которая сможет выдавать коины, канал, в который будут отправляться '
                          'заказы через buye, канал, в котором доступно казино',
                    inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}give <Упоминание пользователя> <Сумма>**',
                                   value='Выдать деньги пользователю', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}take <Упоминание пользователя> <Сумма(Либо all для '
                                        f'обнуления '
                                        f'счёта)>**',
                                   value='Забрать деньги у пользователя', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}give-role <Упоминание роли> <Сумма>**',
                                   value='Выдать деньги пользователю', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}take-role <Упоминание роли> <Сумма(Либо all для '
                                        f'обнуления '
                                        f'счёта)>**',
                                   value='Забрать деньги у пользователя', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}add-shop <Упоминание роли> <Цена>**',
                                   value='Добавить роль в магазин', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}start_money**',
                                   value='Стартовый баланс при входе на сервер', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}start_money set <Количество>**',
                                   value='Установить стартовый баланс при входе на сервер', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}del_games <Упоминание пользователя>**',
                                   value='Удалить все активные игры для определённого пользователя', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}add-else <Цена> <То, что вы хотите добавить в '
                                        f'магазин>**',
                                   value='Добавить какой-либо предмет в магазин'
                                         '(примечание: после добавление предмету будет '
                                         'выдан id, buye **1** - id выделен',
                                   inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}remove-else <id>**',
                                   value='Удалить какой-либо предмет из магазина', inline=False)
                self.emb.add_field(name=f'**{settings["prefix"]}remove-shop <Упоминание роли>**',
                                   value='Удалить роль из магазина', inline=False)
                await inter.response.send_message(embed=self.emb)
            else:
                await inter.response.send_message("У вас нет прав для использования этой команды")
        elif arg.value == "casino":
            self.row12 = "3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36"
            self.row22 = "2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35"
            self.row32 = "1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34"
            self.emb = discord.Embed(title="Команды бота:")
            self.emb.add_field(name=f'Как работает rust casino?',
                               value='Если простым языком, то Вы ставите какую-либо сумму '
                                     '(эта сумма с Вас снимается) на '
                                     'число ( '
                                     'либо 1, либо 3, либо 5, либо 10, либо 20), если выпадает число 1, то ставка '
                                     'умножается в '
                                     '2 раза, если 3, то в 3 раза, если 5, то в 5 раз и тд, '
                                     'чем меньше число - тем больше шанс на выигрыш', inline=False)
            self.emb.add_field(name=f'А если сложным языком?',
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
            self.emb.add_field(name=f'Как работает coinflip с ботом?',
                               value=f"Ну тут всё проще. Вы прописываете {settings['prefix']}coinflip <сумма>"
                                     f"дальше программа выбирает n число(1 или 2), "
                                     f"если выпадает 1 - побеждаете Вы, и сумма, "
                                     f"которую Вы поставили, умножается в 2 раза, если выпадает 2 - вы проигрываете",
                               inline=False)
            self.emb.add_field(name=f'Как работает coinflip с другим человеком?',
                               value=f"Тут всё немного сложнее. Вы прописываете {settings['prefix']}coinflip <сумма> "
                                     f"<упоминание второго игрока>, а второй игрок прописывает "
                                     f"{settings['prefix']}accept <упоминание первого игрока(Вас)>. "
                                     f"После этого программа также выбирает 2 числа, "
                                     f"если выпадает 1, то побеждаете Вы, "
                                     f"если 2, то Ваш противник", inline=False)
            self.emb.add_field(name=f'Команды коинфлипа на двух игроков',
                               value=f"**{settings['prefix']}coinflip <сумма> "
                                     f"<упоминание второго игрока>** - старт коинфлипа\n"
                                     f"**{settings['prefix']}accept <упоминание игрока>** - принять коинфлип\n"
                                     f"**{settings['prefix']}reject <упоминание игрока>** - отклонить коинфлип\n"
                                     f"**{settings['prefix']}games** - все Ваши активные игры\n"
                                     f"**{settings['prefix']}del_games** - отклонить все активные игры", inline=False)
            self.emb.add_field(name=f"Как работает казино 777?",
                               value=f"Вы ставите ставку, программа генерирует 3 ряда чисел\n"
                                     f"**Случаи выигрыша:**\n"
                                     f"Строка с +, три одинаковых числа в ряд\n"
                                     f"Три одинаковых числа по диагонали\n"
                                     f"**Во сколько раз умножается выигрыш?**\n"
                                     f"Три восьмёрки - в 2 раза\n"
                                     f"Три нуля - в 3 раза\n"
                                     f"Три семёрки - в 5 раз\n"
                                     f"Три единицы - вы ничего не теряете, но и ничего не получаете", inline=False)
            self.emb.add_field(name=f"Как работает roll?",
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
                                            settings['prefix'], self.row12, self.row22, self.row32
                                        )
                               )
            self.emb.add_field(name=f"Как работает fail?",
                               value=f"Вы ставите на определённый коэффициент, "
                                     f"если программа выдаёт коэффициент выше Вашего"
                                     f" - Вы выиграли, и Ваша ставка умножается на Ваш коэффициент", inline=False)
            await inter.response.send_message(embed=self.emb)
        elif arg.value == "me_pls:(":
            if inter.user.id == 401555829620211723:
                await inter.response.send_message(
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
                    "{settings['prefix']}develop_stats <Параметр (lb, slb)> <Параметр (on, off)> - ну тут понятно"
                )
        elif arg.value == "new_year":
            self.emb = discord.Embed(title="Команды Нового года")
            self.emb.add_field(name=f'**{settings["prefix"]}presents**',
                               value='Все ваши подарки', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}present <упоминание игрока> <количество>**',
                               value='Подарить кому-то подарок', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}open <Аргумент>**',
                               value='Открыть подарок\nАргументы: all - открыть все подарки, '
                                     'число - определённое количество',
                               inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}foodshop**',
                               value='Магазин еды', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}food**',
                               value='Ваша еда', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}use <Номер из foodshop>**',
                               value='Использовать еду', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}buyfood <Номер из foodshop> <Количество>**',
                               value='Купить еду', inline=False)
            await inter.response.send_message(embed=self.emb)

        elif arg.value == "tests":
            if inter.user.id == 401555829620211723 or inter.user.id == 608314233079201834:
                self.row12 = "3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36"
                self.row22 = "2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35"
                self.row32 = "1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34"

                self.emb = discord.Embed(title="Команды бета тестеров:")
                self.emb.add_field(name=f'**{settings["prefix"]}roll <Ставка> <Цифра или аргумент>**',
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
                                               self.row12, self.row22, self.row32
                                           ), inline=False)
                await inter.response.send_message(embed=self.emb)

        elif arg.value == "user":
            self.emb = discord.Embed(title="Команды бота:")
            self.emb.add_field(name=f'**{settings["prefix"]}info**',
                               value='За что выдают коины', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}cash <Упоминание пользователя>**',
                               value='Узнать баланс', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}send <Упоминание пользователя> <Сумма>**',
                               value='Перевести деньги', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}shop**',
                               value='Открыть магазин', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}buy <Упоминание роли>**',
                               value='Купить роль', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}rust_casino <Ставка> <Число(1, 3, 5, 10, 20)>**',
                               value=f'Казино, для подробной информации **{settings["prefix"]}help casino**',
                               inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}fail <Ставка> <Коэффициент>**',
                               value=f'Fail, для подробной информации **{settings["prefix"]}help casino**',
                               inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}777 <Ставка>**',
                               value=f'Казино 777, для подобной информации **{settings["prefix"]}help casino**',
                               inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}roll <Ставка> <Аргумент>**',
                               value=f'Рулетка, для подобной информации **{settings["prefix"]}help casino**',
                               inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}stats <Упоминание пользователя>**',
                               value=f'Посмотреть статистику',
                               inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}buye <Номер товара>**',
                               value='Купить другой товар сервера', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}bank**',
                               value='Узнать баланс на счету', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}bank add <Сумма>**',
                               value='Положить деньги на счёт', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}bank take <Сумма>**',
                               value='Снять деньги со счёта', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}levels**',
                               value='Информация о левелах', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}lvl_up**',
                               value='Поднять себе левл', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}lb**',
                               value='Рейтинг богачей сервера', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}lb chat**',
                               value='Рейтинг чата сервера', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}lb voice**',
                               value='Рейтинг голосовых каналов сервера', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}slb**',
                               value='Общий баланс сервера', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}del_games**',
                               value='Удалить все активные игры', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}promo <Промокод>**',
                               value='Активировать промокод', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}promo_create <Сумма>**',
                               value='Создать промокод', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}promocodes <Промокод>**',
                               value='Все Ваши промокоды(писать в личные сообщения)', inline=False)
            self.emb.add_field(name=f'**{settings["prefix"]}card**',
                               value='Получить вашу карточку', inline=False)
            self.month = int(datetime.today().strftime('%m'))
            self.day = int(datetime.today().strftime('%d'))
            if self.month == 2 and self.day == 14:
                self.emb.add_field(name=f'**{settings["prefix"]}val_open <аргумент>**',
                                   value='Открыть валентинки\n'
                                         'Аргументы: all - открыть все валентинки, число - определённое количество',
                                   inline=False)
            self.emb.add_field(name='Помощь для администрации',
                               value=f'**{settings["prefix"]}help admin** - помощь для администрации', inline=False)
            await inter.response.send_message(embed=self.emb)
        else:
            self.emb = discord.Embed(title="Команды бота:")
            self.emb.add_field(name='Ошибка',
                               value=f'Аргумент неверен!', inline=False)
            await inter.response.send_message(embed=self.emb)
