import sqlalchemy

from ..session import SqlAlchemyBase

__all__ = ("Guild",)


class Guild(SqlAlchemyBase):
    __tablename__ = 'guilds'
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False
    )
    guild_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    members = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
