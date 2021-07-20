from .models import Player, Match, Team
from . import db
import logging
import random


def simulate_match(match_id, bo=3.0) -> None:
    """Function to simulate a match. Default is best-of-3 (bo=3.0)."""

    match = Match.query.filter_by(id=match_id).first()

    team1_players = get_players(match.team1_id)
    team2_players = get_players(match.team2_id)

    team1_stats = get_team_stats(team1_players)
    team2_stats = get_team_stats(team2_players)

    win_count_team1 = 0
    win_count_team2 = 0

    while win_count_team1 < (bo / 2.0) and win_count_team2 < (bo / 2.0):
        eff_stats_team1 = get_effective_team_stats(team1_stats)
        eff_stats_team2 = get_effective_team_stats(team2_stats)

        if eff_stats_team1 > eff_stats_team2:
            win_count_team1 += 1
        else:
            win_count_team2 += 1

    if win_count_team1 > win_count_team2:
        match.winner = match.team1_id
    elif win_count_team1 < win_count_team2:
        match.winner = match.team2_id
    else:
        match.winner = 0

    match.status = "finished"

    logging.info(f"Match {match.id} ({match.team1_name} vs. {match.team2_name} finished."
                 f"Winnerteam: {match.winner}")

    db.session.commit()

    logging.info(f"DB updated after finishing match {match.id}")






def get_players(team_id: int) -> list[Player]:
    """Get all players of selected team"""

    players = Player.query.filter_by(team_id=team_id).order_by(Player.position.asc()).all()

    return players


def get_team_stats(players: list[Player]) -> dict[int]:
    """Calculate total stats of the team."""

    team_stats = {}

    total_reaction = 0
    total_mechanical_skill = 0
    total_tactical_skill = 0
    total_game_knowledge = 0

    for player in players:
        total_reaction += player.reaction
        total_mechanical_skill += player.mechanical_skill
        total_tactical_skill += player.tactical_skill
        total_game_knowledge += player.game_knowledge

    team_stats.update(
        {"reaction": total_reaction,
         "mechanical_skill": total_mechanical_skill,
         "tactical_skill": total_tactical_skill,
         "game_knowledge": total_game_knowledge})

    return team_stats


def get_effective_team_stats(team_stats: dict) -> int:
    """Calculate effective stats. Return sum of ("randomized") stat (depending on the teams form on the day)"""

    stats_sum = 0

    for value in team_stats.values():
        stats_sum += value * random.uniform(0.5, 1.5)

    return stats_sum

