# NOTE: THIS FILE CAN AND SHOULD BE COMMITTED WHEN CHANGES ARE PRESENT.

# This is a list of all environment keys that should exist. This file does not contain the actual keys.
# A duplicate file called environment.py should exist with the same keys and contain the actual key values.

# Set the Slack bot token for the slack API.
SLACK_BOT_TOKEN = "<your_token_here>"

# Used to validate incoming requests.
SLACK_SIGNING_SECRET = "<your_token_here>"

# Slack channel IDs. You can get these from the channel URL. They start with a C.
ANNOUNCEMENTS_CID = "<slack_channel_id>"
WORKOUTS_CID = "<slack_channel_id>"
