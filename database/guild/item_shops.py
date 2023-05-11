import sqlalchemy

from database.session import SqlAlchemyBase

__all__ = ("ShopRole",)


class ShopRole(SqlAlchemyBase):
    __tablename__ = 'shop'
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
    item_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    item_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    item_cost = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False,
        default=0
    )
