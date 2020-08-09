import os

from flask import Flask
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy
from slack import WebClient

from environment import SLACK_BOT_TOKEN

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
client = WebClient(token=SLACK_BOT_TOKEN)
db = SQLAlchemy()
executor = Executor()


def create_app():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.getcwd() + "/tribeB.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    db.create_all(app=app)
    executor.init_app(app)

    from bot.slash_commands import slash_commands

    app.register_blueprint(slash_commands)

    from bot.routes import routes

    app.register_blueprint(routes)

    return app
