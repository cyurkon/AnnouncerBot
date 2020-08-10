from os import getenv

from flask import Flask
from flask_executor import Executor
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from slack import WebClient

# These emojis will be tracked on practice announcements.
EMOJIS = {
    "michael_c_smile": "On Time",
    "confused_conner": "Late w/ Excuse",
    "sleepy_eric": "Absent w/ Excuse",
    "gorilla": "Injured",
}
# Used for calculating practice points in attendance statistics.
POINTS = {
    "On Time": 1,
    "Late w/ Excuse": 0.75,
    "Late w/o Excuse": 0.5,
    "Absent w/ Excuse": 0.25,
    "Injured": 0.25,
}
client = WebClient(token=getenv("SLACK_BOT_TOKEN"))
db = SQLAlchemy()
executor = Executor()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    if app.config["ENV"] == "production":
        app.config.from_object("bot.config.ProdConfig")
    elif app.config["ENV"] == "development":
        app.config.from_object("bot.config.DevConfig")

    db.init_app(app)
    db.create_all(app=app)
    executor.init_app(app)
    migrate.init_app(app, db)

    from bot.slash_commands import slash_commands

    app.register_blueprint(slash_commands)

    from bot.routes import routes

    app.register_blueprint(routes)

    return app
