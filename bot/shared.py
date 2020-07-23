from flask_sqlalchemy import SQLAlchemy
from slack import WebClient
from environment import SLACK_BOT_TOKEN

db = SQLAlchemy()
client = WebClient(token=SLACK_BOT_TOKEN)
