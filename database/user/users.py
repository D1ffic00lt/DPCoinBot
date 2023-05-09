import sqlalchemy

from ..session import SqlAlchemyBase

__all__ = ("User",)


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        nullable=False,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
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

    def __str__(self):
        return "User(id={0})".format(
            self.id
        )
