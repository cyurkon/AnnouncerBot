import csv

from flask import make_response, request

from bot import client, executor
from bot.models import Player, Practice
from bot.slash_commands import slash_commands
from bot.validate_request import validate_request


@slash_commands.route("/statistics", methods=["POST"])
@validate_request(is_admin_only=True)
def statistics():
    """Open the statistics modal for the caller."""
    caller = request.form.to_dict()["user_id"]
    executor.submit(generate_statistics, caller)
    return make_response("", 200)


def generate_statistics(caller):
    table = []
    # Create headers for report
    practices = [
        f"{practice.date}\n{practice.time}"
        for practice in Practice.query.order_by(Practice.date).all()
    ]
    headers = [
        "\nName",
        "\nPractice Points",
        "\nOutside Activities",
        "Total\nPower Level",
    ] + practices
    # Iterate through players and compare their attendance history to the headers.
    for player in Player.query.all():
        attendance = {
            f"{record.date}\n{record.time}": record.status for record in player.attendance
        }
        row = [
            player.name,
            player.get_practice_points(),
            player.num_activities,
            player.get_power_level(),
        ] + [attendance.get(practice, "Absent w/o Excuse") for practice in practices]
        table.append(row)

    # Upload file to caller's DM.
    channel = client.conversations_open(users=[caller])["channel"]["id"]
    with open("report.csv", "w", newline="") as f:
        wr = csv.writer(f, delimiter=",")
        wr.writerow(headers)
        wr.writerows(table)
    with open("report.csv", "rb") as f:
        client.files_upload(channels=channel, filename="report.csv", filetype="csv", file=f)
