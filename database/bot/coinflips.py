import sqlalchemy

from database.session import SqlAlchemyBase

__all__ = ("CoinFlip",)


class CoinFlip(SqlAlchemyBase):
    __tablename__ = 'coinflips'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    first_player_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    second_player_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
    guild_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    first_player_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    second_player_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    cash = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False
    )
    date = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )