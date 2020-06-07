import os
from flask import Flask, request, make_response
import json
import requests
from .modals import practice_modal

app = Flask(__name__)
announcement = {
    "time": "",
    "date": "",
    "location": "",
    "is_tournament_roster": False,
    "comments": ""
}


def format_announcement(time, date, location, is_tournament_roster, comments):
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
    api_url = "https://slack.com/api/chat.postMessage"
    api_data = {
        "token": os.environ['SLACK_BOT_TOKEN'],
        "channel": "announcements",
        "text": format_announcement(data["time"], data["date"], data["location"],
                                    data["is_tournament_roster"], data["comments"])
    }
    requests.post(api_url, data=api_data)

@app.route('/slack/events', methods=['POST'])
def practice_announcement():
    if "command" in request.form and request.form["command"] == "/practice":
        api_url = 'https://slack.com/api/views.open'
        trigger_id = request.form.get('trigger_id')
        api_data = {
            "token": os.environ['SLACK_BOT_TOKEN'],
            "trigger_id": trigger_id,
            "view": json.dumps(practice_modal)
        }
        requests.post(api_url, data=api_data)
    elif "payload" in request.form:
        payload = json.loads(request.form["payload"])
        if payload["type"] == "block_actions" and payload["view"]["callback_id"] == "practice modal":
            submitted_data = payload["actions"][0]
            if submitted_data["type"] == "datepicker":
                announcement["date"] = submitted_data["selected_date"]
            elif submitted_data["type"] == "static_select":
                announcement["location"] = submitted_data["selected_option"]["text"]["text"]
            else:
                announcement["is_tournament_roster"] = True
        elif payload["type"] == "view_submission" and payload["view"]["callback_id"] == "practice modal":
            submitted_data = payload["view"]["state"]["values"]
            announcement["time"] = submitted_data["time_block"]["time"]["value"]
            announcement["comments"] = submitted_data["comments_block"]["comments"]["value"]
            send_announcement(announcement);
        return make_response("", 200)
    return make_response()