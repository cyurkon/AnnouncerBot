import json
from flask import make_response, request
from bot import app
from bot.shared import db, client
from bot.tables import Practice, Attendance
from bot.validate_request import validate_request


IV_URL = "bot/modals/mattend/initial_view.json"
TS_URL = "bot/modals/mattend/time_select.json"
WD_URL = "bot/modals/mattend/wrong_date.json"
FV_URL = "bot/modals/mattend/final_view.json"
DV_URL = "bot/modals/mattend/deleted_view.json"


@app.route("/slack/commands/mattend", methods=["POST"])
@validate_request(is_admin_only=True)
def manual_attendance():
    """Open the manual attendance modal for the caller."""
    with open(IV_URL) as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)


def submit_change(metadata):
    record = Attendance.query.filter_by(
        pid=metadata["pid"], date=metadata["date"], time=metadata["time"]
    ).first()
    if record and metadata["status"] == "Absent w/o Excuse":
        db.session.delete(record)
    elif record:
        record.status = metadata["status"]
    elif metadata["status"] != "Absent w/o Excuse":
        Attendance(**metadata)
    db.session.commit()


def delete_practice(metadata):
    Attendance.query.filter_by(date=metadata["date"], time=metadata["time"]).delete()
    Practice.query.filter_by(date=metadata["date"], time=metadata["time"]).delete()
    db.session.commit()


def json_load(URL):
    with open(URL) as f:
        return json.load(f)


def update_mattend_modal(payload):
    """
    Updates the /mattend modal as different options are selected.

    Metadata can be passed between views using the "private_metadata" field.
    """
    metadata = json.loads(payload["view"]["private_metadata"])
    if payload["type"] == "block_actions":
        view = {}
        data = payload["actions"][0]
        if data["type"] == "datepicker":
            # When a date is chosen, display all practice times found for that date.
            # If none are found, display an error message.
            metadata["date"] = data["selected_date"]
            view = json_load(IV_URL)
            view["blocks"][0]["accessory"]["initial_date"] = metadata["date"]
            times = Practice.query.filter_by(date=metadata["date"]).all()
            if not times:
                view["blocks"].append(json_load(WD_URL))
            else:
                view["blocks"].append(json_load(TS_URL))
        elif data["type"] == "external_select":
            # When a time is chosen, load the next view where attendance adjustments can be made.
            metadata["time"] = data["selected_option"]["value"]
            view = json_load(FV_URL)
            view["blocks"][0]["text"][
                "text"
            ] = "Adjusting attendance for event on {date} at {time}.".format(**metadata)
        elif data["type"] == "button":
            # Delete event button pressed.
            delete_practice(metadata)
            view = json_load(DV_URL)
        view["private_metadata"] = json.dumps(metadata)
        client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
    elif payload["type"] == "view_submission":
        values = payload["view"]["state"]["values"]
        metadata["pid"] = values["player_select"]["player_select"]["selected_option"]["value"]
        metadata["status"] = values["status_select"]["status_select"]["selected_option"]["value"]
        submit_change(metadata)
