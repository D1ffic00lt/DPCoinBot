import sqlalchemy

from database.session import SqlAlchemyBase

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
    name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False,
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
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
