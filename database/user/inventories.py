import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("Inventory",)


class Inventory(SqlAlchemyBase):
    __tablename__ = "inventories"
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.user_id"),
        nullable=False
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("guilds.guild_id"),
        nullable=False,
    )
    new_year_prises = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    valentines = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    user = orm.relationship("User", back_populates="inventories")
    guild = orm.relationship("Guild")
