import sqlalchemy

from database.session import SqlAlchemyBase

__all__ = ("Card",)


class Card(SqlAlchemyBase):
    __tablename__ = "cards"
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    verification = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    developer = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    coder = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    coin = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )