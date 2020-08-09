from flask import Blueprint

routes = Blueprint("routes", __name__, url_prefix="/slack")

from . import events, options_load
