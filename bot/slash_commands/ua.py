import json
from flask import make_response, request
from bot import app
from bot.shared import db, client
from bot.tables import Practice, Attendance


IV_URL = "bot/modals/ua/initial_view.json"
TS_URL = "bot/modals/ua/time_select.json"
WD_URL = "bot/modals/ua/wrong_date.json"
FV_URL = "bot/modals/ua/final_view.json"
ED_URL = "bot/modals/ua/deleted.json"
sessions = {}


class Update:
    """Defines an attendance update"""

    def __init__(self):
        self.pid = ""
        self.date = ""
        self.time = ""
        self.status = ""


def update_view(user, payload):
    session = sessions[user]
    if payload["type"] == "block_actions":
        data = payload["actions"][0]
        if data["type"] == "datepicker":
            session.date = data["selected_date"]
            times = Practice.query.filter_by(date=session.date).all()
            with open(IV_URL) as initial_view, open(TS_URL) as time_select, open(
                WD_URL
            ) as wrong_date:
                view = json.load(initial_view)
                view["blocks"][0]["accessory"]["initial_date"] = session.date
                if not times:
                    view["blocks"].append(json.load(wrong_date))
                else:
                    view["blocks"].append(json.load(time_select))
                client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
        elif data["type"] == "external_select":
            if data["action_id"] == "time_select":
                session.time = data["selected_option"]["text"]["text"]
                textbox = "Adjusting attendance for event on {} at {}".format(
                    session.date, session.time
                )
                with open(FV_URL) as final_view:
                    view = json.load(final_view)
                    view["blocks"][0]["text"]["text"] = textbox
                    client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
            else:
                session.pid = data["selected_option"]["value"]
        elif data["type"] == "button":
            Attendance.query.filter_by(
                pid=session.pid, date=session.date, time=session.time
            ).delete()
            Practice.query.filter_by(date=session.date, time=session.time).delete()
            db.session.commit()
            with open(ED_URL) as deleted:
                client.views_update(view_id=payload["view"]["id"], view=json.loads(deleted.read()))
        else:
            session.status = data["selected_option"]["text"]["text"]
    elif payload["type"] == "view_submission":
        record = Attendance.query.filter_by(
            pid=session.pid, date=session.date, time=session.time
        ).first()
        if record and session.status == "Absent w/o Excuse":
            # Delete user from DB
            db.session.delete(record)
        elif record:
            # Adjust attendance type
            record.status = session.status
        elif session.status != "Absent w/o Excuse":
            # Insert player into attendance DB
            Attendance(pid=session.pid, date=session.date, time=session.time, status=session.status)
        db.session.commit()
    sessions[user] = session


@app.route("/slack/commands/ua", methods=["POST"])
def update_attendance():
    user = request.form["user_id"]
    sessions[user] = Update()
    with open(IV_URL) as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)
