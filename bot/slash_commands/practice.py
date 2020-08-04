import json
from flask import request, make_response
from bot import app
from bot.shared import client
from bot.tables import Practice
from environment import ANNOUNCEMENTS_CID


@app.route("/slack/commands/practice", methods=["POST"])
def practice():
    with open("bot/modals/practice.json") as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)


def format_announcement(modal):
    """Formats and returns practice announcement text"""
    return (
        "{roster}"
        "*******************************************\n"
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


def submit_announcement(payload):
    """Sends values to format_announcement() and submits result to 'announcements' channel"""
    values = payload["view"]["state"]["values"]
    modal = {
        "time": values["time"]["time"]["value"],
        "date": values["date"]["date"]["selected_date"],
        "location": values["location"]["location"]["selected_option"]["value"],
        "roster": values["roster"]["roster"]["selected_option"]["value"],
    }
    # this try block is needed because of a bug in the Slack API. I reported it and will remove this when it's fixed.
    try:
        modal["comments"] = values["comments"]["comments"].get("value", "")
    except KeyError:
        modal["comments"] = ""
    message = format_announcement(modal)
    response = client.chat_postMessage(channel=ANNOUNCEMENTS_CID, text=message)
    Practice(timestamp=response["ts"], date=modal["date"], time=modal["time"])
