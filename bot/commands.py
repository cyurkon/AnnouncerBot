import json
from flask import request, make_response
from bot.modals import PRACTICE_MODAL
from bot import app
from bot.shared import db, client
from bot.tables import Player, Practice, Attendance
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
    Practice(response["ts"], announcement.date, announcement.time)


@app.route("/slack/commands/attendance", methods=["POST"])
def attendance():
    untracked_practices = Practice.query.filter_by(is_tracked=False).all()
    for untracked_practice in untracked_practices:
        response = client.reactions_get(
            channel=ANNOUNCEMENTS_CID, timestamp=untracked_practice.timestamp
        )
        reactions = response["message"]["reactions"]
        for reaction in reactions:
            if reaction["name"] in ["michael_c_smile", "confused_conner", "gorilla"]:
                for pid in reaction["users"]:
                    Attendance(pid, untracked_practice.date, untracked_practice.time)
        untracked_practice.is_tracked = True
    db.session.commit()
    return make_response("", 200)


@app.route("/slack/commands/upt", methods=["POST"])
def update_player_table():
    Player.query.delete()
    players = client.users_list()["members"]
    for player in players:
        if not player["is_bot"] and player["id"] != "USLACKBOT" and not player["deleted"]:
            pid = player["id"]
            name = player["profile"]["real_name"]
            is_admin = player["is_admin"]
            Player(pid, name, is_admin)
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

            if "value" in submitted_data["comments_block"]["comments"]:
                announcements[user].comments = submitted_data["comments_block"]["comments"]["value"]
            send_announcement(user)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
