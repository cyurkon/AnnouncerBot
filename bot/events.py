import json
from flask import request, make_response
from bot import app
from bot.slash_commands.practice import update_announcement_modal
from bot.slash_commands.mattend import update_mattend_modal


@app.route("/slack/events", methods=["POST"])
def events():
    """Handles workspace events sent to app's /slack/events url"""
    if request and "payload" in request.form:
        payload = json.loads(request.form["payload"])
        user = payload["user"]["id"]
        # event comes from /practice modal
        if payload["view"]["callback_id"] == "practice modal":
            update_announcement_modal(user, payload)
        # event comes from /mattend modal
        elif payload["view"]["callback_id"] in [
            "initial_mattend_view",
            "final_mattend_view",
            "deleted_mattend_view",
        ]:
            update_mattend_modal(user, payload)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
