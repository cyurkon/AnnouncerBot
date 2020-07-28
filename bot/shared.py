from flask_sqlalchemy import SQLAlchemy
from slack import WebClient
from environment import SLACK_BOT_TOKEN

# db is declared here rather than __init__.py to prevent circular imports.
db = SQLAlchemy()
client = WebClient(token=SLACK_BOT_TOKEN)
# This dictionary maps users to their partially-completed modals and is
# required so that multiple people can use slash commands at the same time.
modals = {}
