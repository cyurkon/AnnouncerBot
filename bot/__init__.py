import os
from flask import Flask
from bot.shared import db

app = Flask(__name__)
# Do not move these imports. Flask requires all files that use route decorators to be imported AFTER the app is created.
import bot.events
import bot.options_load
import bot.slash_commands.practice
import bot.slash_commands.attendance
import bot.slash_commands.upt
import bot.slash_commands.ua

app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.getcwd() + "/tribeB.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)
db.create_all(app=app)
