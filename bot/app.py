import json
import os
from flask import Flask, request, make_response
from slack import WebClient
from .modals import PRACTICE_MODAL

from environment import SLACK_BOT_TOKEN, ANNOUNCEMENTS_CID

app = Flask(__name__)
client = WebClient(token=SLACK_BOT_TOKEN)

# Maps users to their partially completed announcements before they are posted to the workspace
announcements = {}

# Previous post identifiers used for attendance taking
previous_post_ts = []


class Announcement:
    """Defines a channel announcement"""

    def __init__(self):
        self.time = ""
        self.date = ""
        self.location = ""
        self.is_tournament_roster = False
        self.comments = ""


def format_announcement(time, date, location, is_tournament_roster, comments):
    """Formats and returns announcement text"""
    roster = "*TOURNAMENT and RESERVE ROSTER PRACTICE ONLY*\n" if is_tournament_roster else ""
    comments = "" if comments == "N" else comments
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
    ann = announcements[user]
    message = format_announcement(
        ann.time, ann.date, ann.location, ann.is_tournament_roster, ann.comments
    )
    response = client.chat_postMessage(channel=ANNOUNCEMENTS_CID, text=message)
    previous_post_ts.append(response["ts"])


@app.route("/slack/commands/attendance", methods=["POST"])
def attendance():
    while previous_post_ts:
        timestamp = previous_post_ts.pop()
        response = client.reactions_get(channel=ANNOUNCEMENTS_CID, timestamp=timestamp)
        reactions = response["message"]["reactions"]
        for reaction in reactions:
            message = "{0} -- users: {1}".format(reaction["name"], ",".join(reaction["users"]))
            client.chat_postMessage(channel=ANNOUNCEMENTS_CID, text=message)
    return make_response("", 200)


@app.route("/slack/commands/practice", methods=["POST"])
def practice():
    user = request.form["user_id"]
    announcements[user] = Announcement()
    client.views_open(trigger_id=request.form["trigger_id"], view=json.dumps(PRACTICE_MODAL))
    return make_response("", 200)


@app.route("/slack/events", methods=["POST"])
def events():
    """Handles workspace events sent to app's /slack/events url"""
    if "payload" in request.form:
        payload = json.loads(request.form["payload"])
        user = payload["user"]["id"]
        # user interacts with the datepicker, location select, or roster checkbox
        if (
            payload["type"] == "block_actions"
            and payload["view"]["callback_id"] == "practice modal"
        ):
            submitted_data = payload["actions"][0]
            if submitted_data["type"] == "datepicker":
                announcements[user].date = submitted_data["selected_date"]
            elif submitted_data["type"] == "static_select":
                announcements[user].location = submitted_data["selected_option"]["text"]["text"]
            else:
                announcements[user].is_tournament_roster = True
        # user submits form
        elif (
            payload["type"] == "view_submission"
            and payload["view"]["callback_id"] == "practice modal"
        ):
            submitted_data = payload["view"]["state"]["values"]
            announcements[user].time = submitted_data["time_block"]["time"]["value"]
            announcements[user].comments = submitted_data["comments_block"]["comments"]["value"]
            send_announcement(user)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
