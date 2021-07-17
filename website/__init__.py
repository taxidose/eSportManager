from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import logging

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "blubb"  # TODO: CHANGE IN PRODUCTION!
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/admin")

    #from .views import page_not_found

    #app.register_error_handler(404, page_not_found)

    from .models import User

    create_db(app)

    from website.utility import update_market

    with app.app_context():
        update_market()

    login_manager = LoginManager()
    login_manager.login_view = "auth.landing"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_db(app):
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all(app=app)
        logging.info("Created Database")