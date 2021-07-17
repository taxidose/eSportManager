from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Player, Team
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