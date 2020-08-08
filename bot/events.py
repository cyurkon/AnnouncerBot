import json

from flask import make_response, request

from bot import app
from environment import WORKOUTS_CID
from bot.shared import db
from bot.slash_commands.dac import update_database
from bot.slash_commands.mattend import update_mattend_modal
from bot.slash_commands.practice import submit_announcement
from bot.slash_commands.statistics import generate_statistics
from bot.tables import Player
from bot.validate_request import validate_request


@app.route("/slack/events", methods=["POST"])
@validate_request()
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
        # submitted from /statistics modal
        elif payload["view"]["callback_id"] == "/statistics":
            generate_statistics(payload)
        elif payload["view"]["callback_id"] == "/dac":
            update_database(payload)
    elif request and "event" in request.json:
        event = request.json["event"]
        if event["type"] == "message" and event["text"] and event["channel"] == WORKOUTS_CID:
            track_workout(event)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)


def track_workout(event):
    pids = {event["user"]}
    text_blocks = event["blocks"][0]["elements"][0]["elements"]
    for text_block in text_blocks:
        if text_block["type"] == "user":
            pids.add(text_block["user_id"])
    for pid in pids:
        if player := Player.query.filter_by(pid=pid).first():
            player.num_activities += 1
    db.session.commit()
