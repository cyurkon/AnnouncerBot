import json

from flask import make_response, request

from bot import app
from bot.shared import client, db
from bot.tables import Attendance, Player, Practice
from bot.validate_request import validate_request


@app.route("/slack/commands/dac", methods=["POST"])
@validate_request(is_admin_only=True)
def database_admin_console():
    """Open the database administrator console modal for the caller."""
    with open("bot/modals/dac.json") as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)


def update_database(payload):
    if payload["type"] == "block_actions":
        data = payload["actions"][0]
        # User clicks "Update Player Table"
        if data["type"] == "button" and data["action_id"] == "upt":
            update_player_table()
        # User clicks "Clear Database"
        elif data["type"] == "button" and data["action_id"] == "cd":
            clear_database()


def update_player_table():
    """Insert all workspace users into the database's Player table."""
    current_pids = [player.pid for player in Player.query.all()]
    users = client.users_list()["members"]
    for user in users:
        pid = user["id"]
        if not user["is_bot"] and pid != "USLACKBOT" and not user["deleted"]:
            name = user["profile"]["real_name"]
            is_admin = user["is_admin"]
            if pid not in current_pids:
                Player(pid=pid, name=name, admin=is_admin)
            else:
                prev = Player.query.filter_by(pid=pid).first()
                prev.name = name
                prev.admin = is_admin
                db.session.commit()


def clear_database():
    Attendance.query.delete()
    Player.query.delete()
    Practice.query.delete()
    update_player_table()
    db.session.commit()
