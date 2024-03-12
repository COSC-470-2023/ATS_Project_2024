import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

load_dotenv()

username = os.getenv("ATS_DBMS_USER")
password = os.getenv("ATS_DBMS_PASS")
hostname = os.getenv("ATS_DBMS_HOST")
database = os.getenv("ATS_DBMS_DATABASE")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{username}:{password}@{hostname}/{database}"
    )
    app.secret_key = "secret_key"  # TODO: MUST change this key to something better and store elsewhere

    # Create app context
    app.app_context().push()
    db.init_app(app)

    # Import blueprints
    from .auth import auth
    from .views import views
    from .data_export import data_export
    from .job_scheduling import job_scheduling

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(data_export, url_prefix="/data-export")
    app.register_blueprint(job_scheduling, url_prefix="/job-scheduling")

    from .models import Users

    # Setup login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # User loader callback. User by Flask-Login for authentaction handling
    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    return app
