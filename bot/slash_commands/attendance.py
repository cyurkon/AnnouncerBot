from flask import make_response
from bot import app
from bot.shared import db, client, validate_request
from bot.tables import Practice, Attendance
from environment import ANNOUNCEMENTS_CID

emojis = {
    "michael_c_smile": "On Time",
    "confused_conner": "Late w/ Excuse",
    "sleepy_eric": "Absent w/ Excuse",
    "gorilla": "Injured",
}


@app.route("/slack/commands/attendance", methods=["POST"])
@validate_request
def attendance():
    untracked_practices = Practice.query.filter_by(is_tracked=False).all()
    for untracked_practice in untracked_practices:
        response = client.reactions_get(
            channel=ANNOUNCEMENTS_CID, timestamp=untracked_practice.timestamp
        )
        if "reactions" in response["message"]:
            reactions = response["message"]["reactions"]
            for reaction in reactions:
                if reaction["name"] in emojis:
                    status = emojis[reaction["name"]]
                    for pid in reaction["users"]:
                        Attendance(
                            pid=pid,
                            date=untracked_practice.date,
                            time=untracked_practice.time,
                            status=status,
                        )
        untracked_practice.is_tracked = True
    db.session.commit()
    return make_response("", 200)
