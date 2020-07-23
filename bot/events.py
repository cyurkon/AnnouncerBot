import json
from flask import request, make_response
from bot import app
from bot.slash_commands.practice import update_announcement


@app.route("/slack/events", methods=["POST"])
def events():
    """Handles workspace events sent to app's /slack/events url"""
    if request and "payload" in request.form:
        payload = json.loads(request.form["payload"])
        user = payload["user"]["id"]

        # event comes from a practice modal (interaction with the datepicker, location select, or roster checkbox)
        if payload["view"]["callback_id"] == "practice modal":
            update_announcement(user, payload)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
