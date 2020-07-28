import json
from flask import make_response, request
from bot import app
from bot.shared import db, client, modals
from bot.tables import Practice, Attendance


IV_URL = "bot/modals/mattend/initial_view.json"
TS_URL = "bot/modals/mattend/time_select.json"
WD_URL = "bot/modals/mattend/wrong_date.json"
FV_URL = "bot/modals/mattend/final_view.json"
DV_URL = "bot/modals/mattend/deleted_view.json"


def submit_change(user):
    modal = modals[user]
    record = Attendance.query.filter_by(
        pid=modal["pid"], date=modal["date"], time=modal["time"]
    ).first()
    if record and modal["status"] == "Absent w/o Excuse":
        db.session.delete(record)
    elif record:
        record.status = modal["status"]
    elif modal["status"] != "Absent w/o Excuse":
        Attendance(pid=modal["pid"], date=modal["date"], time=modal["time"], status=modal["status"])
    db.session.commit()
    modals.pop(user)


def update_mattend_modal(user, payload):
    modal = modals[user]
    if payload["type"] == "block_actions":
        data = payload["actions"][0]
        if data["type"] == "datepicker":
            modal["date"] = data["selected_date"]
            times = Practice.query.filter_by(date=modal["date"]).all()
            with open(IV_URL) as initial_view:
                view = json.load(initial_view)
                view["blocks"][0]["accessory"]["initial_date"] = modal["date"]
                if not times:
                    with open(WD_URL) as wrong_date:
                        view["blocks"].append(json.load(wrong_date))
                else:
                    with open(TS_URL) as time_select:
                        view["blocks"].append(json.load(time_select))
                client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
        elif data["type"] == "external_select" and data["action_id"] == "time_select":
            modal["time"] = data["selected_option"]["value"]
            with open(FV_URL) as final_view:
                view = json.load(final_view)
                view["blocks"][0]["text"][
                    "text"
                ] = "Adjusting attendance for event on {date} at {time}".format(**modal)
                client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
        elif data["type"] == "external_select" and data["action_id"] == "player_select":
            modal["pid"] = data["selected_option"]["value"]
        elif data["type"] == "button":
            Attendance.query.filter_by(date=modal["date"], time=modal["time"]).delete()
            Practice.query.filter_by(date=modal["date"], time=modal["time"]).delete()
            db.session.commit()
            with open(DV_URL) as deleted_view:
                client.views_update(
                    view_id=payload["view"]["id"], view=json.loads(deleted_view.read())
                )
            modals.pop(user)
        elif data["type"] == "static_select":
            modal["status"] = data["selected_option"]["value"]
    elif payload["type"] == "view_submission":
        submit_change(user)


@app.route("/slack/commands/mattend", methods=["POST"])
def manual_attendance():
    user = request.form["user_id"]
    modals[user] = {"date": "", "time": "", "pid": "", "status": ""}
    with open(IV_URL) as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)
