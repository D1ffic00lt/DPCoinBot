import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("User",)


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
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

    def __str__(self):
        return "User(id={0})".format(
            self.user_id
        )
