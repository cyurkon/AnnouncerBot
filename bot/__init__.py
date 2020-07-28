import os
from flask import Flask
from bot.shared import db

app = Flask(__name__)
# Do not move these imports. Flask requires all files that use route decorators to be imported AFTER the app is created.
import bot.events
import bot.options_load

# from bot.slash_commands import *
# For some reason this wildcard import ignores the attendance and upt files (this might be a bug).
# You can view this by uncommenting the code below and placing it after the imports.
# import sys
# print(sys.modules.keys())
import bot.slash_commands.attendance
import bot.slash_commands.mattend
import bot.slash_commands.practice
import bot.slash_commands.upt

app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.getcwd() + "/tribeB.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
db.init_app(app)
db.create_all(app=app)
