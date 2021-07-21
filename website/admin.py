from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Player, Team, User, Match
from . import db


admin = Blueprint("admin", __name__)


@login_required
@admin.route("/")
@admin.route("/info")
def info():
    if not current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if not current_user.is_admin:
        return redirect(url_for("views.home"))

    return "<h1>ADMIN</h1>"


@login_required
@admin.route("/users")
def users():
    if not current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if not current_user.is_admin:
        return redirect(url_for("views.home"))

    all_users = User.query.all()

    return render_template("/admin/users.html")


@login_required
@admin.route("/teams")
def teams():
    if not current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if not current_user.is_admin:
        return redirect(url_for("views.home"))



    return "<h1>team-management/h1>"


@login_required
@admin.route("/players")
def players():
    if not current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if not current_user.is_admin:
        return redirect(url_for("views.home"))

    return "<h1>player-management/h1>"


@login_required
@admin.route("/match")
def match_management():
    if not current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if not current_user.is_admin:
        return redirect(url_for("views.home"))

    return "<h1>match-management/h1>"



