import sqlalchemy

from database.session import SqlAlchemyBase

__all__ = ("Online",)


class Online(SqlAlchemyBase):
    __tablename__ = 'online'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
    time = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )