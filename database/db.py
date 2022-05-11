import sqlite3

from sqlite3 import Cursor

from ..templates.helperfunction import *


class Database:
    @ignore_exceptions
    def __init__(self, filename: str) -> None:
        self.connection = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
            Name                         VARCHAR (255) NOT NULL,
            ID                           INT NOT NULL,
            Cash                         BIGINT DEFAULT 0 NOT NULL,
            Reputation                   INT DEFAULT 0 NOT NULL,
            Lvl                          INT DEFAULT 0 NOT NULL,
            GuildID                      INT NOT NULL,
            CoinFlipsCount               INT DEFAULT 0 NOT NULL,
            CoinFlipsWinsCount           INT DEFAULT 0 NOT NULL,
            CoinFlipsLosesCount          INT DEFAULT 0 NOT NULL,
            RustCasinos                  INT DEFAULT 0 NOT NULL, 
            RustCasinoWinsCount          INT DEFAULT 0 NOT NULL, 
            RustCasinoLoses              INT DEFAULT 0 NOT NULL,
            RollsCount                   INT DEFAULT 0 NOT NULL, 
            RollsWinsCount               INT DEFAULT 0 NOT NULL, 
            RollsLosesCount              INT DEFAULT 0 NOT NULL, 
            FailsCount                   INT DEFAULT 0 NOT NULL, 
            FailsWinsCount               INT DEFAULT 0 NOT NULL, 
            FailsLosesCount              INT DEFAULT 0 NOT NULL,
            ThreeSvensCount              INT DEFAULT 0 NOT NULL, 
            ThreeSvensWinsCount          INT DEFAULT 0 NOT NULL, 
            ThreeSvensLosesCount         INT DEFAULT 0 NOT NULL,
            AllWins                      INT DEFAULT 0 NOT NULL,
            AllLoses                     INT DEFAULT 0 NOT NULL,
            EntireAmountOfWinnings       BIGINT DEFAULT 0 NOT NULL,
            MinutesInVoiceChannels       INT DEFAULT 0 NOT NULL,
            Xp BIGINT                    DEFAULT 0 NOT NULL,
            ChatLevel                    INT DEFAULT 0 NOT NULL,
            MessagesCount                INT DEFAULT 0 NOT NULL,
            CashInBank BIGINT            DEFAULT 0 NOT NULL 
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Shop (
            RoleId                       INT NOT NULL,
            ID                           INT NOT NULL,
            RoleCost                     BIGINT DEFAULT 0 NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Server (
            GuildID                      INT NOT NULL,
            AdministratorRoleID          INT NOT NULL,
            ChannelID                    INT NOT NULL,
            CasinoChannelID              INT NOT NULL,
            CategoryID                   INT NOT NULL,
            Auto                         BOOLEAN NOT NULL,
            StartingBalance              BIGINT DEFAULT 0 NOT NULL,
            BankInterest                 INT DEFAULT 0 NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS ItemsShop (
            ProductID                    INT NOT NULL,
            Name                         VARCHAR (255) NOT NULL,
            ID                           INT NOT NULL,
            Cost                         BIGINT NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Online (
            ID                           INT NOT NULL,
            GuildID                      INT NOT NULL,
            Time                         VARCHAR (255) NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS OnlineStats (
            ID INT NOT NULL,
            GuildID INT NOT NULL,
            Time TIME NOT NULL)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS CoinFlip (
            FirstPlayerID                INT NOT NULL,
            SecondPlayerID               INT NOT NULL,
            FirstPlayerName              VARCHAR (255) NOT NULL,
            SecondPlayerName             VARCHAR (255) NOT NULL,
            GuildID                      INT NOT NULL,
            GuildName                    VARCHAR (255) NOT NULL,
            Cash                         INT NOT NULL,
            Date                         VARCHAR (255) NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Guilds (
            ID                           INT NOT NULL,
            Name                         VARCHAR (255) NOT NULL,
            Members                      INT NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Levels (
           Level                         INT NOT NULL,
           XP                            BIGINT NOT NULL,
           Award                         INT NOT NULL
          )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Achievements (
           Name                         VARCHAR (255) NOT NULL,
           ID                           INT NOT NULL,
           GuildID                      INT NOT NULL,
           Voice_1                      BOOLEAN DEFAULT false NOT NULL,
           Voice_10                     BOOLEAN DEFAULT false NOT NULL,
           Voice_100                    BOOLEAN DEFAULT false NOT NULL,
           Voice_1000                   BOOLEAN DEFAULT false NOT NULL,
           Voice_10000                  BOOLEAN DEFAULT false NOT NULL,
           Voice_100000                 BOOLEAN DEFAULT false NOT NULL,
           Voice_1000000                BOOLEAN DEFAULT false NOT NULL,
           Voice_10000000               BOOLEAN DEFAULT false NOT NULL,
           Lose_3                       BOOLEAN DEFAULT false NOT NULL,
           Lose_10                      BOOLEAN DEFAULT false NOT NULL,
           Lose_20                      BOOLEAN DEFAULT false NOT NULL,
           Loses                        INT DEFAULT 0 NOT NULL,
           Wins_3                       BOOLEAN DEFAULT false NOT NULL,
           Wins_10                      BOOLEAN DEFAULT false NOT NULL,
           Wins_20                      BOOLEAN DEFAULT false NOT NULL,
           Wins                         INT DEFAULT 0 NOT NULL,
           fail_00                      BOOLEAN DEFAULT false NOT NULL
          )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS NewYearEvent (
           Name                         VARCHAR (255) NOT NULL,
           ID                           INT NOT NULL,
           GuildID                      INT NOT NULL,
           MandarinsCount               INT DEFAULT 0 NOT NULL,
           OlivierSaladCount            INT DEFAULT 0 NOT NULL,
           CaesarSaladCount             INT DEFAULT 0 NOT NULL,
           RedСaviarCount               INT DEFAULT 0 NOT NULL,
           BlackСaviarCount             INT DEFAULT 0 NOT NULL,
           SlicedMeatCount              INT DEFAULT 0 NOT NULL,
           DucksCount                   INT DEFAULT 0 NOT NULL,
           SaltedRedFishsCount          INT DEFAULT 0 NOT NULL,
           DobryJuiceCount              INT DEFAULT 0 NOT NULL,
           BabyChampagneCount           INT DEFAULT 0 NOT NULL,
           moodCount                    INT DEFAULT 0 NOT NULL
          )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Inventory (
           Name                         VARCHAR (255) NOT NULL,
           ID                           INT NOT NULL,
           GuildID                      INT NOT NULL,
           NewYearPrises                INT DEFAULT 0 NOT NULL,
           valentine                    INT DEFAULT 0 NOT NULL
           )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Card (
           ID                           INT NOT NULL,
           Verification                 INT DEFAULT 0 NOT NULL,
           Developer                    BOOLEAN DEFAULT false NOT NULL,
           Coder                        BOOLEAN DEFAULT false NOT NULL
           )""")
        self.connection.commit()

    @ignore_exceptions
    def checking_for_user_existence_in_table(self, ID: int, guild_id: int = 0) -> bool:
        if self.cursor.execute("SELECT `Name` FROM `Users` WHERE `ID` = ? AND `GuildID` = ?",
                               (ID, guild_id)).fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def checking_for_guild_existence_in_table(self, guild_id) -> bool:
        if self.cursor.execute("SELECT * FROM `Server` WHERE `GuildID` = ?", (guild_id,)).fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def checking_for_card_existence_in_table(self, ID: int) -> bool:
        if self.cursor.execute("SELECT * FROM `Card` WHERE `ID` = ?", (ID,)).fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def checking_for_achievements_existence_in_table(self, ID: int, guild_id: int) -> bool:
        if self.cursor.execute("SELECT * FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                               (ID, guild_id)).fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def checking_for_inventory_existence_in_table(self, ID: int, guild_id: int) -> bool:
        if self.cursor.execute("SELECT * FROM `Inventory` WHERE `ID` = ? AND `GuildID` = ?",
                               (ID, guild_id)).fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def checking_for_new_year_event_existence_in_table(self, ID: int, guild_id: int) -> bool:
        if self.cursor.execute("SELECT * FROM `NewYearEvent` WHERE `ID` = ? AND `GuildID` = ?",
                               (ID, guild_id)).fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def checking_for_levels_existence_in_table(self) -> bool:
        if self.cursor.execute("SELECT * FROM `Levels` WHERE `Level` = 1").fetchone() is None:
            return False
        return True

    @ignore_exceptions
    def insert_into_users(self, name: str, ID: int, starting_balance, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("INSERT INTO `Users` VALUES (?, ?, ?, 0, 1, ?)",
                                       (name, ID, starting_balance, guild_id))

    @ignore_exceptions
    def insert_into_card(self, ID: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("INSERT INTO `Card` VALUES (?)", (ID,))

    @ignore_exceptions
    def insert_into_achievements(self, name: str, ID: int, guild_id) -> Cursor:
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `Achievements` VALUES (?, ?, ?)", (name, ID, guild_id))

    @ignore_exceptions
    def insert_into_inventory(self, name: str, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `Inventory` VALUES (?, ?, ?)", (name, ID, guild_id))

    @ignore_exceptions
    def insert_into_new_year_event(self, name: str, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute(f"INSERT INTO `NewYearEvent` VALUES (?, ?, ?)", (name, ID, guild_id))

    @ignore_exceptions
    def insert_into_levels(self, Level: int, xp: int, award: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("INSERT INTO `Levels` VALUES (?, ?, ?)", (Level, xp, award))

    @ignore_exceptions
    def get_start_cash(self, guild_id: int = 0) -> int:
        return self.cursor.execute("SELECT `StartingBalance` FROM `Server` "
                                   "WHERE `GuildID` = ?", (guild_id,)).fetchone()[0]

    @ignore_exceptions
    def get_user_name(self, ID: int) -> str:
        return self.cursor.execute(f"SELECT `Name` FROM `Users` WHERE `ID` = ?", (ID,)).fetchone()[0]

    @ignore_exceptions
    def get_cash(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute(f"SELECT `Cash` FROM `Users` "
                                   f"WHERE `ID` = ? AND `GuildID` = ?", (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def update_name(self, name: str, ID: int) -> Cursor:
        with self.connection:
            return self.cursor.execute('UPDATE `Users` SET `Name` = ? WHERE `ID` = ?', (name, ID))

    @ignore_exceptions
    def clear_coinflip(self) -> Cursor:
        with self.connection:
            return self.cursor.execute('DELETE FROM `CoinFlip`')

    @ignore_exceptions
    def server_add(self, Bot) -> None:
        for guild in Bot.guilds:
            for member in guild.members:
                if not self.checking_for_user_existence_in_table(member.id, guild.id):
                    if not self.checking_for_guild_existence_in_table(guild.id):
                        start_cash = 0
                    else:
                        start_cash = self.get_start_cash(guild.id)
                    self.insert_into_users(str(member), member.id, start_cash, guild.id)
                if not self.checking_for_card_existence_in_table(member.id):
                    self.insert_into_card(member.id)
                if not self.checking_for_achievements_existence_in_table(member.id, guild.id):
                    self.insert_into_achievements(str(member), member.id, guild.id)
                if not self.checking_for_inventory_existence_in_table(member.id, guild.id):
                    self.insert_into_inventory(str(member), member.id, guild.id)
                if not self.checking_for_new_year_event_existence_in_table(member.id, guild.id):
                    self.insert_into_new_year_event(str(member), member.id, guild.id)
                if self.get_user_name(member.id) != member:
                    self.update_name(str(member), member.id)

    @ignore_exceptions
    def voice_create_stats(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("INSERT INTO `OnlineStats` VALUES (?, ?, ?)", (ID, guild_id, get_time()))

    @ignore_exceptions
    def voice_create(self, ID: int, guild_id: int, voice_create_stats: bool = False) -> Cursor:
        if voice_create_stats:
            self.voice_create_stats(ID, guild_id)
        with self.connection:
            return self.cursor.execute("INSERT INTO `Online` VALUES (?, ?, ?)", (ID, guild_id, get_time()))

    @ignore_exceptions
    def add_coins(self, ID: int, guild_id: int, cash: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Users` SET `Cash` + ? WHERE `ID` = ? AND `GuildID` = ?",
                                       (cash, ID, guild_id))

    @ignore_exceptions
    def take_coins(self, ID: int, guild_id: int, cash: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Users` SET `Cash` - ? WHERE `ID` = ? AND `GuildID` = ?",
                                       (cash, ID, guild_id))

    @ignore_exceptions
    def create_voice_stats(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("INSERT INTO `OnlineStats` VALUES (?, ?, ?)", (ID, guild_id, get_time()))

    @ignore_exceptions
    def add_coins_to_the_bank(self, ID: int, guild_id: int, cash: int) -> Cursor:
        with self.connection:
            self.take_coins(ID, guild_id, cash)
            return self.cursor.execute("UPDATE  `Users` SET `CashInBank` = `CashInBank` + ? "
                                       "WHERE `ID` = ? AND `GuildID` = ?", (cash, ID, guild_id))

    @ignore_exceptions
    def take_coins_from_the_bank(self, ID: int, guild_id: int, cash: int) -> Cursor:
        with self.connection:
            self.add_coins(ID, guild_id, cash)
            return self.cursor.execute("UPDATE `Users` SET `CashInBank` = `CashInBank` - ? "
                                       "WHERE `ID` = ? AND `GuildID` = ?", (cash, ID, guild_id))

    @ignore_exceptions
    def get_loses_count(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Loses` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def get_wins_count(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Wins` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def get_three_losses_in_row_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Lose_3` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_three_losses_in_row_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Lose_3` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_ten_losses_in_row_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Lose_10` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_ten_losses_in_row_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Lose_10` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_twenty_losses_in_row_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Lose_20` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_twenty_losses_in_row_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Lose_20` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_three_wins_in_row_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Wins_3` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_three_wins_in_row_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Wins_3` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_ten_wins_in_row_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Wins_10` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_ten_wins_in_row_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Wins_10` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_twenty_wins_in_row_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Wins_20` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_twenty_wins_in_row_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Wins_20` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def update_user_stats1(self, arg: str, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Users` SET ? = ?+ 1 WHERE `ID` = ? AND `GuildID` = ?",
                                       (arg, arg, ID, guild_id))

    @ignore_exceptions
    def update_user_stats2(self, first_arg: str, second_arg: str, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Users` SET ?? = ?? + 1 WHERE `ID` = ? AND `GuildID` = ?",
                                       (first_arg, second_arg, first_arg, second_arg, ID, guild_id))

    @ignore_exceptions
    def update_user_stats3(self, arg: str, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Users` SET All? = All? + 1 WHERE `ID` = ? AND `GuildID` = ?",
                                       (arg, arg, ID, guild_id))

    @ignore_exceptions
    def update_user_stats4(self, count: int, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Users` SET Count = Count + ? WHERE `ID` = ? AND `GuildID` = ?",
                                       (count, ID, guild_id))

    @ignore_exceptions
    def stats_update_member(
            self,
            ID: int,
            guild_id: int,
            first_arg: str,
            second_arg: str,
            third_arg: str,
            count: int
    ) -> None:
        self.update_user_stats1(first_arg, ID, guild_id)
        self.update_user_stats2(second_arg, third_arg, ID, guild_id)
        self.update_user_stats3(third_arg, ID, guild_id)
        self.update_user_stats4(count, ID, guild_id)

    @ignore_exceptions
    def get_time_from_online_stats(self, ID: int, guild_id: int) -> str:
        return datetime_to_str(self.cursor.execute("SELECT `Time` FROM `OnlineStats` WHERE `ID` = ? AND `GuildID` = ?",
                                                   (ID, guild_id)).fetchone()[0])

    @ignore_exceptions
    def delete_from_online_stats(self, ID: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("DELETE FROM `OnlineStats` WHERE `ID` = ?", (ID,))

    @ignore_exceptions
    def update_minutes_in_voice_channels(self, count: int, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute(
                "UPDATE `Users` SET `MinutesInVoiceChannels` = `MinutesInVoiceChannels` + ? "
                "WHERE `ID` = ? AND `GuildID` = ?", (count, ID, guild_id)
            )

    @ignore_exceptions
    def insert_into_online_stats(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("INSERT INTO `OnlineStats` VALUES (?, ?, ?)",
                                       (ID, guild_id, get_time()))

    @ignore_exceptions
    def get_minutes(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `MinutesInVoiceChannels` FROM `Users` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def get_voice_1_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_1` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_1_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET Voice_1 = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_voice_10_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_10` FROM Achievements WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_10_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Voice_10` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_voice_100_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_100` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_100_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET Voice_100 = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_voice_1000_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_1000` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_1000_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Voice_1000` = true WHERE `ID` = ? AND `GuildID` = ?",
                                       (ID, guild_id))

    @ignore_exceptions
    def get_voice_10000_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_10000` FROM `Achievements` WHERE id = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_10000_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Voice_10000` = true "
                                       "WHERE `ID` = ? AND `GuildID` = ?", (ID, guild_id))

    @ignore_exceptions
    def get_voice_100000_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_100000` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_100000_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Voice_100000` = true "
                                       "WHERE `ID` = ? AND `GuildID` = ?", (ID, guild_id))

    @ignore_exceptions
    def get_voice_1000000_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_1000000` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_1000000_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Voice_1000000` = true "
                                       "WHERE `ID` = ? AND `GuildID` = ?", (ID, guild_id))

    @ignore_exceptions
    def get_voice_10000000_achievement(self, ID: int, guild_id: int) -> int:
        return self.cursor.execute("SELECT `Voice_1000000` FROM `Achievements` WHERE `ID` = ? AND `GuildID` = ?",
                                   (ID, guild_id)).fetchone()[0]

    @ignore_exceptions
    def set_voice_10000000_achievement(self, ID: int, guild_id: int) -> Cursor:
        with self.connection:
            return self.cursor.execute("UPDATE `Achievements` SET `Voice_1000000` = true "
                                       "WHERE `ID` = ? AND `GuildID` = ?", (ID, guild_id))

    @ignore_exceptions
    def add_win(self, ID: int, guild_id: int, null: bool = False):
        with self.connection:
            if null:
                self.cursor.execute("UPDATE `Achievements` SET `Wins` = 0 WHERE `ID` = ? AND `GuildID` = ?",
                                    (ID, guild_id))
            else:
                self.cursor.execute("UPDATE `Achievements` SET `Wins` = `Wins` + 1 WHERE `ID` = ? AND `GuildID` = ?",
                                    (ID, guild_id))

    @ignore_exceptions
    def add_lose(self, ID: int, guild_id: int, null: bool = False):
        with self.connection:
            if null:
                self.cursor.execute("UPDATE `Achievements` SET `Loses` = 0 WHERE `ID` = ? AND `GuildID` = ?",
                                    (ID, guild_id))
            else:
                self.cursor.execute("UPDATE `Achievements` SET `Loses` = `Loses` + 1 WHERE `ID` = ? AND `GuildID` = ?",
                                    (ID, guild_id))

    @ignore_exceptions
    def get_level(self, ID, guild_id):
        return self.cursor.execute("SELECT Lvl FROM `Users` WHERE `GuildID` = ? AND `ID` = ?",
                                   (ID, guild_id)).fetchone()[0]
