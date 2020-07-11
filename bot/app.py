import os
from flask import Flask, request, make_response
import json
import requests
from .modals import PRACTICE_MODAL

app = Flask(__name__)

ANNOUNCEMENTS_CHANNEL_ID = "C014ZBQN82X"
announcements = {}  # Maps users to their partially completed announcements before they are posted to the workspace
previous_post_ts = []  # Previous post identifiers used for attendance taking


class Announcement:
    """Defines a channel announcement"""
    def __init__(self):
        self.time = ""
        self.date = ""
        self.location = ""
        self.is_tournament_roster = False
        self.comments = ""


def post_message(channel, message):
    endpt = "https://slack.com/api/chat.postMessage"
    data = {
        "token": os.environ['SLACK_BOT_TOKEN'],
        "channel": channel,
        "text": message
    }
    return requests.post(endpt, data=data)


def get_reactions(channel, timestamp):
    endpt = 'https://slack.com/api/reactions.get'
    data = {
        "token": os.environ['SLACK_BOT_TOKEN'],
        "channel": channel,
        "timestamp": timestamp
    }
    return requests.post(endpt, data=data)


def open_view(trigger_id, view):
    endpt = 'https://slack.com/api/views.open'
    data = {
        "token": os.environ['SLACK_BOT_TOKEN'],
        "trigger_id": trigger_id,
        "view": view
    }
    return requests.post(endpt, data=data)


def format_announcement(time, date, location, is_tournament_roster, comments):
    """Format and return announcement text"""
    roster = "*TOURNAMENT and RESERVE ROSTER PRACTICE ONLY*\n" if is_tournament_roster else ""
    comments = "" if comments == "N" else comments
    return ("{3}"
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
    message = format_announcement(ann.time, ann.date, ann.location,
                                  ann.is_tournament_roster, ann.comments)
    response = post_message("announcements", message)
    previous_post_ts.append(response.json()["ts"])


@app.route("/slack/commands/attendance", methods=["POST"])
def attendance():
    while previous_post_ts:
        timestamp = previous_post_ts.pop()
        response = get_reactions(ANNOUNCEMENTS_CHANNEL_ID, timestamp)
        reactions = response.json()["message"]["reactions"]
        for reaction in reactions:
            message = reaction["name"] + " -- users: " + ','.join(reaction["users"])
            post_message("announcements", message)
    return make_response("", 200)


@app.route("/slack/commands/practice", methods=["POST"])
def practice():
    user = request.form["user_id"]
    announcements[user] = Announcement()
    open_view(request.form.get('trigger_id'), json.dumps(PRACTICE_MODAL))
    return make_response("", 200)


@app.route('/slack/events', methods=['POST'])
def events():
    """Handles workspace events sent to app's /slack/events url"""
    if "payload" in request.form:
        payload = json.loads(request.form["payload"])
        user = payload["user"]["id"]
        # user interacts with the datepicker, location select, or roster checkbox
        if payload["type"] == "block_actions" and payload["view"]["callback_id"] == "practice modal":
            submitted_data = payload["actions"][0]
            if submitted_data["type"] == "datepicker":
                announcements[user].date = submitted_data["selected_date"]
            elif submitted_data["type"] == "static_select":
                announcements[user].location = submitted_data["selected_option"]["text"]["text"]
            else:
                announcements[user].is_tournament_roster = True
        # user submits form
        elif payload["type"] == "view_submission" and payload["view"]["callback_id"] == "practice modal":
            submitted_data = payload["view"]["state"]["values"]
            announcements[user].time = submitted_data["time_block"]["time"]["value"]
            announcements[user].comments = submitted_data["comments_block"]["comments"]["value"]
            send_announcement(user)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
