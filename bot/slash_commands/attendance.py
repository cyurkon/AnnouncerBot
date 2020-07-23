from flask import make_response
from bot import app
from bot.shared import db, client
from bot.tables import Practice, Attendance
from environment import ANNOUNCEMENTS_CID


@app.route("/slack/commands/attendance", methods=["POST"])
def attendance():
    untracked_practices = Practice.query.filter_by(is_tracked=False).all()
    for untracked_practice in untracked_practices:
        response = client.reactions_get(
            channel=ANNOUNCEMENTS_CID, timestamp=untracked_practice.timestamp
        )
        reactions = response["message"]["reactions"]
        for reaction in reactions:
            if reaction["name"] in ["michael_c_smile", "confused_conner", "gorilla"]:
                for pid in reaction["users"]:
                    Attendance(pid=pid, date=untracked_practice.date, time=untracked_practice.time)
        untracked_practice.is_tracked = True
    db.session.commit()
    return make_response("", 200)
