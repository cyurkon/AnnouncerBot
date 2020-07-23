import os
from flask import Flask
from bot.shared import db

app = Flask(__name__)
import bot.commands

app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.getcwd() + "/tribeB.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)
db.create_all(app=app)
