import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("ShopRole",)


class ShopRole(SqlAlchemyBase):
    __tablename__ = 'shops'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("guilds.guild_id"),
        nullable=False,
    )
    role_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
    role_cost = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False,
        default=0
    )
    guild = orm.relationship("Guild")

