import json

from flask import request

from bot.routes import routes
from bot.slash_commands.mattend import mattend_options_load
from bot.validate_request import validate_request


@routes.route("/options-load-endpoint", methods=["POST"])
@validate_request()
def options_load():
    """Handle external_select payloads sent to app's /slack/options-load-endpoint url."""
    options = {"options": []}
    payload = json.loads(request.form["payload"])
    if payload["view"]["callback_id"] == "/mattend":
        mattend_options_load(payload, options)
    return options
