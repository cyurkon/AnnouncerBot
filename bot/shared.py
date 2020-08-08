from flask_sqlalchemy import SQLAlchemy
from slack import WebClient

from environment import SLACK_BOT_TOKEN


# db is declared here rather than __init__.py to prevent circular imports.
db = SQLAlchemy()
# Used to make Slack API calls.
client = WebClient(token=SLACK_BOT_TOKEN)
# These emojis will be tracked on practice announcements.
EMOJIS = {
    "michael_c_smile": "On Time",
    "confused_conner": "Late w/ Excuse",
    "sleepy_eric": "Absent w/ Excuse",
    "gorilla": "Injured",
}
# Used for calculating practice points in attendance statistics.
POINTS = {
    "On Time": 1,
    "Late w/ Excuse": 0.75,
    "Late w/o Excuse": 0.5,
    "Absent w/ Excuse": 0.25,
    "Injured": 0.25,
}
