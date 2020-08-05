import json
from flask import request, make_response
from bot import app
from bot.slash_commands.practice import submit_announcement
from bot.slash_commands.mattend import update_mattend_modal
from bot.shared import validate_request


@app.route("/slack/events", methods=["POST"])
@validate_request
def events():
    """Dispatch workspace events sent to app's /slack/events url."""
    if request and "payload" in request.form:
        payload = json.loads(request.form["payload"])
        # submitted /practice modal
        if payload["view"]["callback_id"] == "/practice":
            submit_announcement(payload)
        # submitted from /mattend modal
        elif payload["view"]["callback_id"] == "/mattend":
            update_mattend_modal(payload)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
