from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Player, Team
from . import db
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
@views.route("/market")
def market():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    players_on_market = \
        Player.query.filter_by(on_market=True).order_by(Player.position.asc()).order_by(Player.value.asc()).all()

    return render_template("/public/market.html", user=current_user, players=players_on_market)


@login_required
@views.route("/buy/<int:playerid>")
def buy(playerid):
    if not current_user.is_authenticated:
        return redirect(url_for("auth.landing"))

    player = Player.query.filter_by(id=playerid).first()
    buyer_team = Team.query.filter_by(owner_id=current_user.id).first()
    if player.on_market is True:
        player.team_id = buyer_team.id
        player.on_market = False
        db.session.commit()

    return redirect(url_for("views.market"))






