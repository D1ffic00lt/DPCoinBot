import sqlalchemy

from database.session import SqlAlchemyBase

__all__ = ("Achievement",)


class Achievement(SqlAlchemyBase):
    __tablename__ = 'achievements'
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    voice_level_1_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_2_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_3_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_4_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_5_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_6_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_7_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    voice_level_8_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    defeat_level_1_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    defeat_level_2_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    defeat_level_3_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    losses = sqlalchemy.Column(
        sqlalchemy.Integer,
        default=0
    )
    wins_level_1_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    wins_level_2_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    wins_level_3_achievement = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )
    dropping_zero_in_fail = sqlalchemy.Column(
        sqlalchemy.Boolean,
        default=False,
        nullable=False
    )