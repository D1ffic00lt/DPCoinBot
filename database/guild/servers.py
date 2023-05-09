import sqlalchemy
from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("ServerSettings",)


class ServerSettings(SqlAlchemyBase):
    __tablename__ = 'server_settings'
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    administrator_role_if = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    channel_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    casino_channel_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    auto_setup = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False,
        default=1
    )
    bank_interest = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    starting_balance = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False,
        default=0
    )
