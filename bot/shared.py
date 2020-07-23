from flask_sqlalchemy import SQLAlchemy
from slack import WebClient
from environment import SLACK_BOT_TOKEN

# These are declared here rather than __init__.py to prevent circular imports.
db = SQLAlchemy()
client = WebClient(token=SLACK_BOT_TOKEN)
