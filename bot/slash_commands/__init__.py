from flask import Blueprint

slash_commands = Blueprint("slash_commands", __name__, url_prefix="/slack/commands")

from . import attendance, dac, mattend, practice, statistics
