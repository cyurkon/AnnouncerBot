import json
import requests
from flask import make_response, request
from sqlalchemy import exc

from bot import app, executor
from environment import ANNOUNCEMENTS_CID
from bot.shared import client, db, EMOJIS
from bot.tables import Attendance, Practice
from bot.validate_request import validate_request


@app.route("/slack/commands/attendance", methods=["POST"])
@validate_request(is_admin_only=True)
def attendance():
    """Runs take_attendance on a background thread."""
    resp_url = request.form.to_dict()["response_url"]
    executor.submit(take_attendance, resp_url)
    return make_response("Taking attendance...", 200)


def take_attendance(resp_url):
    """Iterate through all untracked practices and record emoji responses."""
    untracked_practices = Practice.query.filter_by(is_tracked=False).all()
    for untracked_practice in untracked_practices:
        response = client.reactions_get(
            channel=ANNOUNCEMENTS_CID, timestamp=untracked_practice.timestamp
        )
        reactions = response["message"].get("reactions", [])
        for emoji, status in EMOJIS.items():
            pids = next(
                (reaction["users"] for reaction in reactions if reaction["name"] == emoji), []
            )
            for pid in pids:
                try:
                    Attendance(
                        pid=pid,
                        date=untracked_practice.date,
                        time=untracked_practice.time,
                        status=status,
                    )
                except exc.IntegrityError:
                    db.session.rollback()
        untracked_practice.is_tracked = True
    db.session.commit()
    data = {"text": "Done!", "response_type": "ephemeral"}
    requests.post(resp_url, data=json.dumps(data))
