import hashlib
import hmac
from time import time
from flask import request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from slack import WebClient
from environment import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET


# db is declared here rather than __init__.py to prevent circular imports.
db = SQLAlchemy()
client = WebClient(token=SLACK_BOT_TOKEN)
# This dictionary maps users to their partially-completed modals and is
# required so that multiple people can use slash commands at the same time.
modals = {}


# The following methods are used to verify that incoming requests are from Slack.
# All endpoints should have the @validate_request decorator attached.
# Based on https://github.com/slackapi/python-slack-events-api/blob/main/slackeventsapi/server.py
def verify_signature(request_data, timestamp, signature):
    msg = str.encode("v0:" + str(timestamp) + ":") + request_data
    request_hash = (
        "v0=" + hmac.new(str.encode(SLACK_SIGNING_SECRET), msg, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(request_hash, signature)


def is_valid():
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    if timestamp is None or abs(time() - int(timestamp)) > 60 * 5:
        return False
    signature = request.headers.get("X-Slack-Signature")
    if signature is None or not verify_signature(request.get_data(), timestamp, signature):
        return False
    return True


def validate_request(endpoint):
    @wraps(endpoint)
    def wrapper():
        assert is_valid()
        return endpoint()

    return wrapper
