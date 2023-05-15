import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("OnlineStats",)


class OnlineStats(SqlAlchemyBase):
    __tablename__ = 'online_stats'
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
    time = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    user = orm.relationship("User")
    guild = orm.relationship("Guild")
