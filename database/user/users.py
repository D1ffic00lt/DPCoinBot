import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("User",)


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("guilds.guild_id"),
        nullable=False

    )
    cash = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        default=0,
        nullable=False
    )
    cash_in_bank = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        default=0,
        nullable=False
    )
    guild = orm.relationship("Guild")
    achievements = orm.relationship("Achievement", back_populates="user", lazy="selectin")
    inventories = orm.relationship("Inventory", back_populates="user", lazy="selectin")
    new_year_events = orm.relationship("NewYearEvent", back_populates="user", lazy="selectin")
    users_stats = orm.relationship("UserStats", back_populates="user", lazy="selectin")
    cards = orm.relationship("Card", back_populates="user", lazy="selectin")

    def __str__(self):
        return "User(id={0})".format(
            self.user_id
        )

    def __repr__(self):
        return "User(id={0}, guild_id={1})".format(
            self.user_id, self.guild_id
        )
