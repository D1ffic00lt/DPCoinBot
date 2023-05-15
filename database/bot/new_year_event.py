import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("NewYearEvent",)


class NewYearEvent(SqlAlchemyBase):
    __tablename__ = 'new_year_events'
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
    mandarins_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    olivier_salad_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    caesar_salad_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    red_caviar_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    black_caviar_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    sliced_meat_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    ducks_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    salted_red_fish_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    dobry_juice_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    baby_champagne_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    mood_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0
    )
    user = orm.relationship("User", back_populates="new_year_events")
    guild = orm.relationship("Guild")
