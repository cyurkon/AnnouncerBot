import json
from flask import request
from bot import app
from bot.shared import modals, validate_request
from bot.tables import Player, Practice


@app.route("/slack/options-load-endpoint", methods=["POST"])
@validate_request
def options_load():
    """Handles external_select payloads sent to app's /slack/options-load-endpoint url"""
    payload = json.loads(request.form["payload"])
    user = payload["user"]["id"]
    action_id = payload["action_id"]
    options = {"options": []}
    if action_id == "time_select":
        for practice in Practice.query.filter_by(date=modals[user]["date"]).all():
            options["options"].append(
                {"text": {"type": "plain_text", "text": practice.time}, "value": practice.time}
            )
    elif action_id == "player_select":
        for player in Player.query.all():
            options["options"].append(
                {"text": {"type": "plain_text", "text": player.name}, "value": player.pid}
            )
    return options
