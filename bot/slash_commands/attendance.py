import json
import requests
from flask import make_response, request
from sqlalchemy import exc

from bot import client, db, executor, EMOJIS
from bot.models import Attendance, Player, Practice
from bot.slash_commands import slash_commands
from bot.validate_request import validate_request
from environment import ANNOUNCEMENTS_CID


@slash_commands.route("/attendance", methods=["POST"])
@validate_request(is_admin_only=True)
def attendance():
    """Run take_attendance on a background thread."""
    resp_url = request.form.to_dict()["response_url"]
    executor.submit(take_attendance, resp_url)
    return make_response("Taking attendance...", 200)


def take_attendance(resp_url):
    """Iterate through all untracked practices and record emoji responses."""
    practices = Practice.query.filter_by(is_tracked=False).all()
    for practice in practices:
        reactions = client.reactions_get(channel=ANNOUNCEMENTS_CID, timestamp=practice.timestamp)[
            "message"
        ].get("reactions", [])
        for emoji, status in EMOJIS.items():
            # Retrieve all users that reacted with this emoji
            pids = next(
                (reaction["users"] for reaction in reactions if reaction["name"] == emoji), []
            )
            for pid in pids:
                try:
                    Attendance(
                        pid=pid, date=practice.date, time=practice.time, status=status,
                    )
                # If the user has already reacted with another emoji, ignore this one
                # and send an error message.
                except exc.IntegrityError:
                    db.session.rollback()
                    player = Player.query.filter_by(pid=pid).first()
                    text = (
                        f"{player.name} reacted with more than one emoji"
                        f" for the practice on {practice.date} at {practice.time}."
                    )
                    data = {"text": text, "response_type": "ephemeral"}
                    requests.post(resp_url, data=json.dumps(data))
        practice.is_tracked = True
    db.session.commit()
    data = {"text": "Done!", "response_type": "ephemeral"}
    requests.post(resp_url, data=json.dumps(data))
