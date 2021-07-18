from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Player, Team, User
from . import db
from sqlalchemy.sql import func
import logging


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






