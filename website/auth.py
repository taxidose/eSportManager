from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Team
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import logging


auth = Blueprint("auth", __name__)


@auth.route("/landing")
def landing():
    return render_template("/public/landing.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nameoremail = request.form.get("nameoremail")

        password = request.form.get("password")

        user = User.query.filter_by(email=nameoremail).first()

        if not user:  # if no user is found by mail, names will be checked
            user = User.query.filter_by(nickname=nameoremail).first()

        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully", category="success")
                login_user(user, remember=True)
                logging.info(f"{user.nickname} logged in.")
                return redirect(url_for("views.home"))
            else:
                logging.info(f"{user.nickname} entered incorret password.")
                flash("Incorrect password!", category="error")
        else:
            flash("Account does not exist", category="error")
            logging.info(f"Tried to log in with not existing account.")

    return render_template("public/login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.landing"))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        team_name = request.form.get("teamname")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(nickname=name).first()

        if user:
            flash("Email already exists", category="error")
        elif user_name:
            flash("Name already exists", category="error")
        elif len(email) < 4:
            flash("Email not valid", category="error")
        elif len(name) < 3:
            flash("Name must be longer than 3 characters", category="error")
        elif password1 != password2:
            flash("Passwords dont match", category="error")
        elif len(password1) < 5:
            flash("Password mus be at least 5 characters", category="error")
        elif len(team_name) < 1:
            flash("Teamname not valid", category="error")
        else:
            new_user = User(nickname=name, email=email, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            new_team = Team(name=team_name, owner=new_user)
            db.session.add(new_team)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account created", category="success")
            logging.info(f"Account {name} created.")

            return redirect(url_for("views.home"))

    return render_template("public/sign-up.html", user=current_user)
