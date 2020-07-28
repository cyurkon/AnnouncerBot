import json
from flask import request, make_response
from bot import app
from bot.shared import client, modals
from bot.tables import Practice
from environment import ANNOUNCEMENTS_CID


def update_announcement_modal(user, payload):
    modal = modals[user]
    if payload["type"] == "block_actions":
        data = payload["actions"][0]
        if data["type"] == "datepicker":
            modal["date"] = data["selected_date"]
        elif data["type"] == "static_select":
            modal["location"] = data["selected_option"]["value"]
        elif data["type"] == "checkboxes":
            modal["type"] = "*TOURNAMENT and RESERVE ROSTER PRACTICE ONLY*\n"
    elif payload["type"] == "view_submission":
        data = payload["view"]["state"]["values"]
        modal["time"] = data["time_block"]["time"]["value"]
        # Use get method when API is updated
        if "comments_block" in data and "value" in data["comments_block"]["comments"]:
            modal["comments"] = data["comments_block"]["comments"]["value"]
        submit_announcement(user)


def format_announcement(modal):
    """Formats and returns announcement text"""
    return (
        "{type}"
        "********************************************\n"
        "Practice from *{time}*, *{date}*\n"
        "{location}\n"
        "================================\n"
        ":michael_c_smile:: react if you will be coming\n"
        ":confused_conner:: react if you will be coming but late\n"
        ":sleepy_eric:: react if you will not be coming\n"
        ":gorilla:: react if you will be coming but not playing\n"
        "********************************************\n"
        "{comments}".format(**modal)
    )


def submit_announcement(user):
    """Sends data to format_announcement() and submits result to 'announcements' channel"""
    modal = modals[user]
    message = format_announcement(modal)
    response = client.chat_postMessage(channel=ANNOUNCEMENTS_CID, text=message)
    Practice(timestamp=response["ts"], date=modal["date"], time=modal["time"])
    modals.pop(user)


@app.route("/slack/commands/practice", methods=["POST"])
def practice():
    user = request.form["user_id"]
    modals[user] = {"type": "", "time": "", "date": "", "location": "", "comments": ""}
    with open("bot/modals/practice.json") as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)
