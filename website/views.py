from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Player, Team, User, Match
from . import db
from sqlalchemy.sql import func
import logging
from .match_sim import simulate_match

views = Blueprint("views", __name__)


@login_required
@views.route("/")
@views.route("/index")
@views.route("/home")
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    return render_template("/public/index.html", user=current_user)


@login_required
@views.route("/team")
def team():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    user_team = Team.query.filter_by(owner_id=current_user.id).first()
    team_players = Player.query.filter_by(team_id=user_team.id).order_by(Player.position.asc()).all()
    team_value = db.session.query(func.sum(Player.value)).filter_by(team_id=user_team.id).all()[0][0]

    # show teamwert: 0 € instad of None €
    if not team_value:
        team_value = 0

    user_info = User.query.filter_by(id=current_user.id).first()

    return render_template("/public/team.html", user=current_user, players=team_players,
                           team=user_team, teamvalue=team_value, userinfo=user_info)


@login_required
@views.route("/sell/<int:playerid>")
def sell(playerid):
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    player = Player.query.filter_by(id=playerid).first()
    seller_team = Team.query.filter_by(owner_id=current_user.id).first()
    user = User.query.filter_by(id=current_user.id).first()

    # only sell if player is in current user's team

    try:
        if player.team_id == seller_team.id:
            player.team_id = None
            user.money += player.value
            player.on_market = True
            db.session.commit()

    # exception gets thrown when /sell/playerid failed (e.g. invalid player id)
    except AttributeError as e:
        flash(f"Verkauf fehlgeschlagen ({e.__doc__})", category="error")

    finally:
        return redirect(url_for("views.team"))


@login_required
@views.route("/buy/<int:playerid>")
def buy(playerid):
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    player = Player.query.filter_by(id=playerid).first()
    buyer_team = Team.query.filter_by(owner_id=current_user.id).first()
    user = User.query.filter_by(id=current_user.id).first()

    try:
        if player.on_market is True:
            player.team_id = buyer_team.id
            player.on_market = False
            user.money -= player.value
            db.session.commit()

    # exception gets thrown when /buy/playerid failed (e.g. invalid player id)
    except AttributeError as e:
        flash(f"Kauf fehlgeschlagen ({e.__doc__})", category="error")

    finally:
        return redirect(url_for("views.market"))


@login_required
@views.route("/market")
def market():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    players_on_market = \
        Player.query.filter_by(on_market=True).order_by(Player.position.asc()).order_by(Player.value.asc()).all()

    user_info = User.query.filter_by(id=current_user.id).first()

    return render_template("/public/market.html", user=current_user, userinfo=user_info, players=players_on_market)


@login_required
@views.route("/open-matches")
def open_matches():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    # user = User.query.filter_by(id=current_user.id)
    user_team = Team.query.filter_by(owner_id=current_user.id).first()
    open_matches_user = Match.query.filter(
        ((Match.team1_id == user_team.id) | (Match.team2_id == user_team.id)) & Match.status != "finished").all()

    return render_template("public/open-matches.html", user=current_user, openmatches=open_matches_user,
                           userteam=user_team)


@login_required
@views.route("/challenge")
def challenge():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    user_info = User.query.filter_by(id=current_user.id).first()
    user_team = Team.query.filter_by(owner_id=current_user.id).first()

    # all other teams
    teams = Team.query.filter(Team.owner_id != current_user.id).all()

    return render_template("/public/challenge.html", user=current_user, userinfo=user_info,
                           teams=teams, userteam=user_team)


@login_required
@views.route("/match/create/<int:team1_id>-<int:team2_id>")
def create_match(team1_id, team2_id):
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    # check if there is currently an open match pending
    match_pending = Match.query.filter(
        ((Match.team1_id == team1_id) & (Match.team2_id == team2_id) & (Match.status != "finished")) |
        ((Match.team2_id == team1_id) & (Match.team1_id == team2_id) & (Match.status != "finished"))
    ).first()

    # print(f"{match_pending=}")
    # print(f"{match_pending.team1=}")
    # print(f"{match_pending.team2=}")
    # print(f"{match_pending.id=}")
    # print(f"{match_pending.status=}")

    # TODO: activate check after testing
    # if match_pending:
    #     flash("Team kann nicht herausgefordert werden, da noch ein offenes Match existiert.", category="error")
    #     return redirect(url_for("views.challenge"))

    team1 = Team.query.filter_by(id=team1_id).first()
    team2 = Team.query.filter_by(id=team2_id).first()

    new_match = Match(team1_id=team1_id, team2_id=team2_id, team1_name=team1.name, team2_name=team2.name)
    db.session.add(new_match)
    db.session.commit()

    flash("Herausforderung versendet.", category="success")
    logging.info(f"Match between team {team1.name} (id: {team1_id}) & team {team2.name} (id: {team2_id}) created.")

    return redirect(url_for("views.challenge"))


@login_required
@views.route("/match/cancel/<int:matchid>")
def cancel_match(matchid):
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    match = Match.query.filter_by(id=matchid).first()
    user_team = Team.query.filter_by(owner_id=current_user.id).first()

    if match.team1_id != user_team.id and match.team2_id != user_team.id:
        flash("Match kann nicht abgebrochen werden (Userteam nicht beteiligt).")
        return redirect(url_for("views.open_matches"))

    db.session.delete(match)
    db.session.commit()

    flash(f"Match gegen {match.team1_name} abgelehnt.", category="success")
    logging.info(f"Match {match.id} ({match.team1_name} vs. {match.team2_name} canceled")

    return redirect(url_for("views.open_matches"))


@login_required
@views.route("/match/accept/<int:matchid>")
def accept_match(matchid):
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    match = Match.query.filter_by(id=matchid).first()
    user_team = Team.query.filter_by(owner_id=current_user.id).first()

    if match.team1_id != user_team.id and match.team2_id != user_team.id:
        flash("Match kann nicht angenommen werden (Userteam nicht beteiligt).")
        return redirect(url_for("views.open_matches"))

    match.status = "accepted"
    db.session.commit()

    flash(f"Match gegen {match.team1_name} angenommen.", category="success")
    logging.info(f"Match {match.id} ({match.team1_name} vs. {match.team2_name} accepted")

    simulate_match(match.id)

    return redirect(url_for("views.open_matches"))


@login_required
@views.route("/match-history")
def match_history():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    user_team = Team.query.filter_by(owner_id=current_user.id).first()
    matches = Match.query.filter(
        ((Match.team1_id == user_team.id) | (Match.team2_id == user_team.id)) & (Match.status == "finished")).order_by(Match.timestamp.desc()).all()

    return render_template("/public/match-history.html", user=current_user, matchhistory=matches,
                           userteam=user_team)


def page_not_found(e):
    return render_template('public/404.html', user=current_user), 404
