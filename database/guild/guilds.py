import sqlalchemy

from database.session import SqlAlchemyBase

__all__ = ("Guild",)


class Guild(SqlAlchemyBase):
    __tablename__ = 'guilds'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
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
