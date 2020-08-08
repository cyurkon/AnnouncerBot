import json

from flask import make_response, request
from tabulate import tabulate

from bot import app
from bot.shared import client
from bot.tables import Player, Practice
from bot.validate_request import validate_request


@app.route("/slack/commands/statistics", methods=["POST"])
@validate_request(is_admin_only=True)
def statistics():
    """Open the statistics modal for the caller."""
    with open("bot/modals/statistics.json") as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)


def generate_statistics(payload):
    if payload["type"] == "block_actions":
        data = payload["actions"][0]
        # User requests report.txt
        if data["type"] == "button" and data["action_id"] == ".txt":
            table = []
            # Create headers for report
            header_practices = [
                f"{practice.date}\n{practice.time}"
                for practice in Practice.query.order_by(Practice.date).all()
            ]
            headers = [
                "\nName",
                "\nPractice Points",
                "\nOutside Activities",
                "Total\nPower Level",
            ] + header_practices
            # Iterate through players and compare their attendance history to the headers.
            for player in Player.query.all():
                row = [
                    player.name,
                    player.get_practice_points(),
                    player.num_activities,
                    player.get_power_level(),
                ]
                attendance = {
                    f"{record.date}\n{record.time}": record.status for record in player.attendance
                }
                for header_practice in header_practices:
                    row.append(attendance.get(header_practice, "Absent w/o Excuse"))
                table.append(row)
            # Upload file to caller's DM.
            user = payload["user"]["id"]
            channel = client.conversations_open(users=[user])["channel"]["id"]
            content = tabulate(table, headers=headers, tablefmt="pretty")
            client.files_upload(
                channels=channel, filename="report.txt", filetype="text", content=content
            )
