from flask import make_response
from bot import app
from bot.shared import client
from bot.tables import Player
from bot.validate_request import validate_request


@app.route("/slack/commands/upt", methods=["POST"])
@validate_request(is_admin_only=True)
def update_player_table():
    """Insert all workspace users into the database's Player table."""
    Player.query.delete()
    players = client.users_list()["members"]
    for player in players:
        if not player["is_bot"] and player["id"] != "USLACKBOT" and not player["deleted"]:
            pid = player["id"]
            name = player["profile"]["real_name"]
            is_admin = player["is_admin"]
            Player(pid=pid, name=name, admin=is_admin)
    return make_response("", 200)
