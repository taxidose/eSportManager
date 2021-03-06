from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    money = db.Column(db.Float(40), default=100_000)
    reg_date = db.Column(db.DateTime(timezone=True), default=func.now())
    is_admin = db.Column(db.Boolean)

    teams = relationship("Team", back_populates="owner", passive_deletes=True)

    def __repr__(self):
        return "<User %r>" % self.nickname


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    owner_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    found_date = db.Column(db.DateTime(timezone=True), default=func.now())

    owner = relationship("User", back_populates="teams", passive_deletes=True)

    def __repr__(self):
        return "<Team %r>" % self.name

    # TODO: implement (team-)moral


class TeamSponsor(db.Model):
    team_name = db.Column(db.String(50), db.ForeignKey("team.name", ondelete="CASCADE"), primary_key=True)
    sponsor_name = db.Column(db.String(50), primary_key=True)
    payment = db.Column(db.Float)

    def __repr__(self):
        return "<Sponsor %r>" % self.sponsor_name


# class Squad(db.Model):
#     id = db.Column(db.Integer, autoincrement=True)
#     name = db.Column(db.String(50), primary_key=True)
#     team = db.Column(db.String(50), db.ForeignKey("team.name", ondelete="CASCADE"), primary_key=True)
#     moral = db.Column(db.Integer)
#     found_date = db.Column(db.DateTime(timezone=True), default=func.now())
#
#     # relationship?
#     team_rel = relationship("Team", back_populates="squads")
#
#     def __repr__(self):
#         return "<Squad %r>" % self.name


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    team1_name = db.Column(db.String, db.ForeignKey("team.name"))
    team2_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    team2_name = db.Column(db.String, db.ForeignKey("team.name"))
    winner = db.Column(db.Integer, db.ForeignKey("team.id"))
    status = db.Column(db.Enum("challenged", "accepted", "finished"), default=("challenged"))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(30))
    name = db.Column(db.String(40))
    bday = db.Column(db.Date)
    nationality = db.Column(db.String(2))
    wealth = db.Column(db.Integer)
    value = db.Column(db.Integer)

    position = db.Column(db.SmallInteger)

    on_market = db.Column(db.Boolean)

    xp = db.Column(db.Integer)
    reaction = db.Column(db.SmallInteger)
    mechanical_skill = db.Column(db.SmallInteger)
    tactical_skill = db.Column(db.SmallInteger)
    game_knowledge = db.Column(db.SmallInteger)

    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "name": self.name,
            "bday": self.bday,
            "nationality": self.nationality,
            "wealth": self.wealth,
            "value": self.value,
            "position": self.position,
            "on_market": self.on_market,
            "xp": self.xp,
            "reaction": self.reaction,
            "mechanical_skill": self.mechanical_skill,
            "tactical_skill": self.tactical_skill,
            "game_knowledge": self.game_knowledge,
            "team_id": self.team_id,
        }


class PlayerSkill(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), primary_key=True)
    skill = db.Column(db.String(20), primary_key=True)
    effect = db.Column(db.String(20))


class PlayerTrait(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), primary_key=True)
    trait = db.Column(db.String(20), primary_key=True)
    effect = db.Column(db.String(20))




