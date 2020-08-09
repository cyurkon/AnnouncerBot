from bot import client, db
from bot.models import Player
from environment import WORKOUTS_CID


def track_workout(event):
    """
    Increment a player's num_activities by one every time they post in the #workouts channel.

    If the player mentions other users in their post, this function will also increment their
    num_activities.
    """
    pids = {event["user"]}
    text_blocks = event["blocks"][0]["elements"][0]["elements"]
    for text_block in text_blocks:
        if text_block["type"] == "user":
            pids.add(text_block["user_id"])
    for pid in pids:
        if player := Player.query.filter_by(pid=pid).first():
            player.num_activities += 1
    db.session.commit()
    client.chat_postEphemeral(channel=WORKOUTS_CID, user=event["user"], text="Workout tracked!")
