import hashlib
import hmac
from functools import wraps
from time import time

from flask import make_response, request

from environment import SLACK_SIGNING_SECRET
from bot.tables import Player


def verify_signature(request_data, timestamp, signature):
    msg = str.encode("v0:" + str(timestamp) + ":") + request_data
    request_hash = (
        "v0=" + hmac.new(str.encode(SLACK_SIGNING_SECRET), msg, hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(request_hash, signature)


def is_valid_request():
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    if timestamp is None or abs(time() - int(timestamp)) > 60 * 5:
        return False
    signature = request.headers.get("X-Slack-Signature")
    if signature is None or not verify_signature(request.get_data(), timestamp, signature):
        return False
    return True


def validate_request(is_admin_only=False):
    """
    Verify that incoming requests are from Slack and that caller has the correct permissions.

    All endpoints should have the @validate_request decorator attached, with is_admin_only set appropriately.
    Based on https://github.com/slackapi/python-slack-events-api/blob/main/slackeventsapi/server.py.
    See https://api.slack.com/authentication/verifying-requests-from-slack for more details.
    """

    def decorator(func):
        @wraps(func)
        def wrapper():
            assert is_valid_request()
            if is_admin_only:
                try:
                    assert Player.is_admin(request.form.to_dict()["user_id"])
                except AssertionError:
                    return make_response("Maybe one day, kiddo.", 200)
            return func()

        # Neat trick to save the original function.
        # wrapper.unwrapped = func
        return wrapper

    return decorator
