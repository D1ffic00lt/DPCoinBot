import discord

from typing import Union
from discord.ext import commands
from discord.utils import get

from botsections.functions.texts import need_settings
from botsections.functions.additions import divide_the_number, get_time, write_log
from database.db import Database

__all__ = (
    "Guild",
)


class Guild(commands.Cog):
    NAME = 'guild module'

    __slots__ = (
        "db", "bot", "found", "admin",
        "casino_channel", "role", "auto",
        "category", "emb", "guild"
    )

    def __init__(self, bot: commands.Bot, db: Database, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.bot = bot
        self.found: bool
        self.auto: int
        self.admin: Union[discord.TextChannel, int]
        self.casino_channel: Union[discord.TextChannel, int]
        self.role: Union[discord.Role, int]
        self.category: Union[discord.CategoryChannel, int]
        self.emb: discord.Embed
        self.guild: discord.Guild
        print(f"[{get_time()}] [INFO]: Guild connected")
        write_log(f"[{get_time()}] [INFO]: Guild connected")

    @commands.command(aliases=["auto_setup"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def __cat_create(self, ctx: commands.context.Context) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            self.guild = ctx.message.guild
            if self.db.checking_for_guild_existence_in_table(ctx.guild.id):
                self.admin, self.casino_channel, self.role, self.auto, self.category = self.db.get_guild_settings(
                    ctx.guild.id
                )
                self.admin = self.bot.get_channel(self.admin)
                self.casino_channel = self.bot.get_channel(self.casino_channel)
                self.role = get(self.guild.roles, id=self.role)
                if self.casino_channel is not None:
                    await self.casino_channel.delete()
                if self.admin is not None:
                    await self.admin.delete()
                if self.role is not None:
                    await self.role.delete()
                if self.auto == 1:
                    self.found = False
                    for category in self.guild.categories:
                        if category.id == self.category:
                            self.category = category
                            self.found = True
                            break
                    if self.found:
                        await self.category.delete()

            self.category = await self.guild.create_category("DPcoinBOT")
            self.casino_channel = await self.guild.create_text_channel(name=f'Casino', category=self.category)
            self.admin = await self.guild.create_text_channel(name=f'shop_list', category=self.category)
            self.role = await self.guild.create_role(name="Coin Manager", colour=discord.Colour.from_rgb(255, 228, 0))
            self.db.delete_from_server(ctx.guild.id)
            self.db.insert_into_server(
                ctx.guild.id, self.role.id, self.admin.id,
                self.casino_channel.id, self.category.id
            )
            await self.admin.set_permissions(self.guild.default_role, read_messages=False, send_messages=False)
            self.emb = discord.Embed(title="Канал для казино")
            self.emb.add_field(
                name=f'Развлекайтесь!',
                value='Да будет анархия!',
                inline=False)
            await self.casino_channel.send(embed=self.emb)
            self.emb = discord.Embed(title="Канал для заказов")
            self.emb.add_field(
                name=f'Настройте его, пожалуйста🥺',
                value='Разрешите каким-то холопам просматривать этот канал, если конечно же хотите:D',
                inline=False)
            await self.admin.send(embed=self.emb)
            self.emb = discord.Embed(title="Категория создана")
            self.emb.add_field(
                name=f'Требуется дополнительная настройка!',
                value=need_settings.format(self.casino_channel.mention, self.admin.mention, self.role.mention),
                inline=False)
            await ctx.reply(embed=self.emb)

    @commands.command(aliases=["start_money"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def __start_money(self, ctx: commands.context.Context, arg: str = None, cash: int = None) -> None:
        if ctx.author.guild_permissions.administrator or ctx.author.id == 401555829620211723:
            if arg == "set":
                if await self.db.cash_check(ctx, cash, max_cash=1000000) or cash == 0:
                    if not self.db.checking_for_guild_existence_in_table(ctx.guild.id):
                        await ctx.reply(
                            f"{ctx.author.mention}, сервер ещё не настроен! "
                            f"Сперва проведите настройку сервера!(auto_setup)"
                        )
                    else:
                        self.db.set_start_cash(cash, ctx.guild.id)
                        await ctx.message.add_reaction('✅')
            elif arg is None:
                if not self.db.checking_for_guild_existence_in_table(ctx.guild.id):
                    await ctx.reply(
                        f"{ctx.author.mention}, сервер ещё не настроен! "
                        f"Сперва проведите настройку сервера!(auto_setup)"
                    )
                else:
                    await ctx.reply(
                        f"На данный момент при входе дают "
                        f"**{divide_the_number(self.db.get_start_cash(ctx.guild.id))}** DP коинов"
                    )
