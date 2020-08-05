from flask import make_response
from bot import app
from bot.shared import db, client
from bot.tables import Practice, Attendance
from environment import ANNOUNCEMENTS_CID
from bot.validate_request import validate_request

emojis = {
    "michael_c_smile": "On Time",
    "confused_conner": "Late w/ Excuse",
    "sleepy_eric": "Absent w/ Excuse",
    "gorilla": "Injured",
}


@app.route("/slack/commands/attendance", methods=["POST"])
@validate_request(is_admin_only=True)
def attendance():
    """Iterate through all untracked practices and record emoji responses."""
    untracked_practices = Practice.query.filter_by(is_tracked=False).all()
    for untracked_practice in untracked_practices:
        response = client.reactions_get(
            channel=ANNOUNCEMENTS_CID, timestamp=untracked_practice.timestamp
        )
        reactions = response["message"].get("reactions", [])
        for emoji, status in emojis.items():
            pids = next(
                (reaction["users"] for reaction in reactions if reaction["name"] == emoji), []
            )
            for pid in pids:
                Attendance(
                    pid=pid,
                    date=untracked_practice.date,
                    time=untracked_practice.time,
                    status=status,
                )
        untracked_practice.is_tracked = True
    db.session.commit()
    return make_response("", 200)
