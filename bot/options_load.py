import json
from flask import request
from bot import app
from bot.slash_commands.ua import date
from bot.tables import Player, Practice


def load_times():
    options = {"options": []}
    for num, practice in enumerate(Practice.query.filter_by(date=date).all()):
        options["options"].append(
            {"text": {"type": "plain_text", "text": practice.time}, "value": str(num)}
        )
    return options


def load_players():
    options = {"options": []}
    for num, player in enumerate(Player.query.all()):
        options["options"].append(
            {"text": {"type": "plain_text", "text": player.name}, "value": str(num)}
        )
    return options


@app.route("/slack/options-load-endpoint", methods=["POST"])
def options_load():
    action_id = json.loads(request.form["payload"])["action_id"]
    return {"time_select": load_times, "player_select": load_players}[action_id]()
