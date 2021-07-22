from .models import Player
from . import db
from faker import Faker
import datetime
from random import randrange
import logging


def create_player(name=None, nickname=None) -> Player:
    """Create a new player instance"""

    fake = Faker()
    if name is None:
        name = fake.name()
    if nickname is None:
        nickname = name.split()[0]  # TODO: generate proper nicknames

    # create random bday between 1980 and 2005
    start_date = datetime.date(year=1980, month=1, day=1)
    end_date = datetime.date(year=2006, month=1, day=1)
    bday = fake.date_between(start_date=start_date, end_date=end_date)
    on_market = True

    nationality = "XX"
    wealth = 0

    xp = randrange(1000)

    position = randrange(1, 6)

    # generate attributes between 0 and 50
    reaction = randrange(51)
    technical_skill = randrange(51)
    tactical_skill = randrange(51)
    game_knowledge = randrange(51)

    # value calculation TODO optimize
    value = int((reaction * 0.5 + technical_skill * 1.5 + tactical_skill * 1.5 + game_knowledge) * xp)

    new_player = Player(nickname=nickname, name=name, bday=bday, on_market=on_market, nationality=nationality,
                        wealth=wealth, xp=xp, position=position, reaction=reaction,
                        mechanical_skill=technical_skill, tactical_skill=tactical_skill,
                        game_knowledge=game_knowledge, value=value)

    return new_player


def update_market(name_list=None, player_amount=50) -> None:
    """Adds players to the db which can be bought (on_market = True). You can pass names which you want to be created."""

    if name_list:
        custom_player = [create_player(name) for name in name_list]
    else:
        custom_player = []

    default_player = [create_player() for _ in range(player_amount - len(custom_player))]

    player_list = default_player + custom_player

    # delete current players on market
    Player.query.filter_by(on_market=True).delete()

    # add player to player table with attribut on_market = True
    db.session.add_all(player_list)
    db.session.commit()

    logging.info(f"{len(player_list)} new players created...")
