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
    
    def __getitem__(self, item):
        _all = [
            self.mandarins_count,
            self.olivier_salad_count,
            self.caesar_salad_count,
            self.red_caviar_count,
            self.black_caviar_count,
            self.sliced_meat_count,
            self.ducks_count,
            self.salted_red_fish_count,
            self.dobry_juice_count,
            self.baby_champagne_count
        ]
        return _all[item]

    def update(self, item, count):
        if item == 0:
            self.mandarins_count += count
        if item == 1:
            self.olivier_salad_count += count
        if item == 2:
            self.caesar_salad_count += count
        if item == 3:
            self.red_caviar_count += count
        if item == 4:
            self.black_caviar_count += count
        if item == 5:
            self.sliced_meat_count += count
        if item == 6:
            self.ducks_count += count
        if item == 7:
            self.salted_red_fish_count += count
        if item == 8:
            self.dobry_juice_count += count
        if item == 9:
            self.baby_champagne_count += count
