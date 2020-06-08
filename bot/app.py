import os
from flask import Flask, request, make_response
import json
import requests
from .modals import practice_modal

app = Flask(__name__)

# TODO: Consider multi-user access to this dictionary -- maybe convert to class
#       and store in dict keyed by userID
announcement = {
    "time": "",
    "date": "",
    "location": "",
    "is_tournament_roster": False,
    "comments": ""
}


def format_announcement(time, date, location, is_tournament_roster, comments):
    """Format and return announcement text"""
    roster = "*TOURNAMENT and RESERVE ROSTER PRACTICE ONLY*\n" if is_tournament_roster else ""
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


def send_announcement(data):
    """Sends data to format_announcement() and submits result to 'announcements' channel"""
    endpt = "https://slack.com/api/chat.postMessage"
    data = {
        "token": os.environ['SLACK_BOT_TOKEN'],
        "channel": "announcements",
        "text": format_announcement(data["time"], data["date"], data["location"],
                                    data["is_tournament_roster"], data["comments"])
    }
    requests.post(endpt, data=data)


@app.route('/slack/events', methods=['POST'])
def practice_announcement():
    """Handles slash commands and workspace events sent to app's /slack/events url"""
    # /practice called by user
    if "command" in request.form and request.form["command"] == "/practice":
        endpt = 'https://slack.com/api/views.open'
        data = {
            "token": os.environ['SLACK_BOT_TOKEN'],
            "trigger_id": request.form.get('trigger_id'),
            "view": json.dumps(practice_modal)
        }
        requests.post(endpt, data=data)
    # modal (partially) submitted
    elif "payload" in request.form:
        payload = json.loads(request.form["payload"])
        # user interacts with the datepicker, location select, or roster checkbox
        if payload["type"] == "block_actions" and payload["view"]["callback_id"] == "practice modal":
            submitted_data = payload["actions"][0]
            if submitted_data["type"] == "datepicker":
                announcement["date"] = submitted_data["selected_date"]
            elif submitted_data["type"] == "static_select":
                announcement["location"] = submitted_data["selected_option"]["text"]["text"]
            else:
                announcement["is_tournament_roster"] = True
        # user submits form
        elif payload["type"] == "view_submission" and payload["view"]["callback_id"] == "practice modal":
            submitted_data = payload["view"]["state"]["values"]
            announcement["time"] = submitted_data["time_block"]["time"]["value"]
            announcement["comments"] = submitted_data["comments_block"]["comments"]["value"]
            send_announcement(announcement)
        # default response
        return make_response("", 200)
    # validates events url
    return make_response(request.json["challenge"])
