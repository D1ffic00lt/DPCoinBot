import sqlalchemy
from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("UserStats",)


class UserStats(SqlAlchemyBase):
    __tablename__ = 'user_stats'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id")
    )
    rating_messages = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        default=0,
        nullable=False
    )
    reputation = sqlalchemy.Column(
        sqlalchemy.Double,
        default=5,
        nullable=False
    )
    xp = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        default=0,
        nullable=False
    )
    chat_lvl = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    coin_flips_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    coin_flips_wins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    rust_casinos_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    rust_casino_wins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    rust_casino_loses_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    rolls_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    rolls_wins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    rolls_loses_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    fails_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    fails_wins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    fails_loses_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    three_sevens_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    three_sevens_wins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    three_sevens_loses_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    all_wins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    all_loses_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    entire_amount_of_winnings = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    minutes_in_voice_channels = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    messages_count = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        default=0,
        nullable=False
    )
    rating_messages_count = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        default=0,
        nullable=False
    )
    user = orm.relationship("User")