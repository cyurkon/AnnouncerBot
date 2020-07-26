import json
from flask import make_response, request
from bot import app
from bot.shared import db, client
from bot.tables import Player, Practice

user = ""
attendance_type = ""
date = ""
IV_URL = "bot/modals/ua/initial_view.json"
TS_URL = "bot/modals/ua/time_select.json"
WD_URL = "bot/modals/ua/wrong_date.json"
FV_URL = "bot/modals/ua/final_view.json"


def update_view(payload):
    global user, attendance_type, date
    if payload["type"] == "block_actions":
        data = payload["actions"][0]
        if data["type"] == "datepicker":
            date = data["selected_date"]
            times = Practice.query.filter_by(date=date).all()
            with open(IV_URL) as initial_view, open(TS_URL) as time_select, open(
                WD_URL
            ) as wrong_date:
                view = json.load(initial_view)
                if not times:
                    view["blocks"].append(json.load(wrong_date))
                else:
                    view["blocks"].append(json.load(time_select))
                client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
        elif data["type"] == "external_select":
            if data["action_id"] == "time_select":
                time = data["selected_option"]["text"]["text"]
                textbox = "Adjusting attendance for event on {} at {}".format(date, time)
                with open(FV_URL) as final_view:
                    view = json.load(final_view)
                    view["blocks"][0]["text"]["text"] = textbox
                    client.views_update(view_id=payload["view"]["id"], view=json.dumps(view))
            else:
                user = data["selected_option"]["text"]["text"]
        else:
            attendance_type = data["selected_option"]["text"]["text"]
    elif payload["type"] == "view_submission":
        if user in [player.name for player in Player.query.all()]:
            # TODO update player
            print("updating player with attributes {} and {}".format(user, attendance_type))
        db.session.commit()


@app.route("/slack/commands/ua", methods=["POST"])
def update_attendance():
    with open(IV_URL) as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)
