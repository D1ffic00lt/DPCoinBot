import sqlalchemy

from ..session import SqlAlchemyBase

__all__ = ("Level",)


class Level(SqlAlchemyBase):
    __tablename__ = 'levels'
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