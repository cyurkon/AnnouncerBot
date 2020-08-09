import json

from flask import make_response, request

from environment import ANNOUNCEMENTS_CID
from bot import client
from bot.models import Practice
from bot.slash_commands import slash_commands
from bot.validate_request import validate_request


@slash_commands.route("/practice", methods=["POST"])
@validate_request(is_admin_only=True)
def practice():
    """Open a practice modal for the caller."""
    with open("bot/static/modals/practice.json") as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)


def format_announcement(modal):
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
    """Send modal to format_announcement() and submit result to 'announcements' channel."""
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
