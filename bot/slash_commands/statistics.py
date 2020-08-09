import csv
import io

from flask import make_response, request

from bot import client, executor
from bot.models import Player, Practice
from bot.slash_commands import slash_commands
from bot.validate_request import validate_request


@slash_commands.route("/statistics", methods=["POST"])
@validate_request(is_admin_only=True)
def statistics():
    """Generate attendance statistics for the caller."""
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
    table.append(["Name", "Practice Points", "Outside Activities", "Total Power Level"] + practices)
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

    # Open DM with caller.
    channel = client.conversations_open(users=[caller])["channel"]["id"]
    # Build CSV without using a file as an intermediary.
    buffer = io.StringIO()
    csv.writer(buffer).writerows(table)
    file = buffer.getvalue().encode()
    buffer.close()
    # DM caller with the file.
    client.files_upload(channels=channel, filename="report.csv", filetype="csv", file=file)
