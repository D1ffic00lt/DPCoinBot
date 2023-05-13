import sqlalchemy

from sqlalchemy import orm

from ..session import SqlAlchemyBase

__all__ = ("Achievement",)


class Achievement(SqlAlchemyBase):
    __tablename__ = 'achievements'
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
    voice_achievements_level = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=False,
        nullable=False
    )  # [1:8]
    defeat_achievements_level = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=False,
        nullable=False
    )  # [1:3]
    losses = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0
    )
    wins = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0
    )
    wins_achievement_level = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=False,
        nullable=False
    )  # [1:3]
    dropping_zero_in_fail = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    user = orm.relationship("User", back_populates="achievements")
    guild = orm.relationship("Guild")
