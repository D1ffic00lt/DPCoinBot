import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("PromoCode",)


class PromoCode(SqlAlchemyBase):
    __tablename__ = "promo_codes"
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        nullable=False
    )
    guild_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("guilds.guild_id"),
        nullable=False,
    )
    code = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    cash = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        nullable=False,
    )
    global_status = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0,
        nullable=False
    )
    user = orm.relationship("User")
    guild = orm.relationship("Guild")
