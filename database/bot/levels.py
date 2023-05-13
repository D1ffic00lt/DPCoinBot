import sqlalchemy

from ..session import SqlAlchemyBase

__all__ = ("Level",)


class Level(SqlAlchemyBase):
    __tablename__ = 'levels'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    level = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    xp = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False
    )
    award = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
