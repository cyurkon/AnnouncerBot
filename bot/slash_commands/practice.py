import json
from flask import request, make_response
from bot import app
from bot.shared import client
from bot.tables import Practice
from environment import ANNOUNCEMENTS_CID

# Maps users to their partially completed announcements before they are posted to the workspace
announcements = {}


class Announcement:
    """Defines a channel announcement"""

    def __init__(self):
        self.time = ""
        self.date = ""
        self.location = ""
        self.is_tournament_roster = False
        self.comments = ""


def update_announcement(user, payload):
    if payload["type"] == "block_actions":
        submitted_data = payload["actions"][0]
        if submitted_data["type"] == "datepicker":
            announcements[user].date = submitted_data["selected_date"]
        elif submitted_data["type"] == "static_select":
            announcements[user].location = submitted_data["selected_option"]["text"]["text"]
        else:
            announcements[user].is_tournament_roster = True
        # user submits form
    elif payload["type"] == "view_submission":
        submitted_data = payload["view"]["state"]["values"]
        announcements[user].time = submitted_data["time_block"]["time"]["value"]

        if "value" in submitted_data["comments_block"]["comments"]:
            announcements[user].comments = submitted_data["comments_block"]["comments"]["value"]
        send_announcement(user)


def format_announcement(announcement):
    """Formats and returns announcement text"""
    time = announcement.time
    date = announcement.date
    location = announcement.location
    is_tournament_roster = announcement.is_tournament_roster
    comments = announcement.comments
    roster = "*TOURNAMENT and RESERVE ROSTER PRACTICE ONLY*\n" if is_tournament_roster else ""
    return (
        "{3}"
        "********************************************\n"
        "Practice from *{0}*, *{1}*\n"
        "{2}\n"
        "================================\n"
        ":michael_c_smile:: react if you will be coming\n"
        ":confused_conner:: react if you will be coming but late\n"
        ":sleepy_eric:: react if you will not be coming\n"
        ":gorilla:: react if you will be coming but not playing\n"
        "********************************************\n"
        "{4}".format(time, date, location, roster, comments)
    )


def send_announcement(user):
    """Sends data to format_announcement() and submits result to 'announcements' channel"""
    announcement = announcements[user]
    message = format_announcement(announcement)
    response = client.chat_postMessage(channel=ANNOUNCEMENTS_CID, text=message)
    Practice(timestamp=response["ts"], date=announcement.date, time=announcement.time)


@app.route("/slack/commands/practice", methods=["POST"])
def practice():
    user = request.form["user_id"]
    announcements[user] = Announcement()
    with open("bot/modals/practice.json") as f:
        client.views_open(trigger_id=request.form["trigger_id"], view=json.loads(f.read()))
    return make_response("", 200)
