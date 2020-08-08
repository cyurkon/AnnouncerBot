# tribeBot
Makes announcements, takes attendance, and handles other miscellaneous tasks.

## Setup
1. Install [ngrok](https://ngrok.com/download) if you plan to test locally (recommended). Add this to your PATH variable so that you can call it from anywhere.
2. Create a new Slack workspace with two channels: `announcements` and `workouts`. When you are in the `announcements` channel, click on the URL and note the channel ID. It starts with a C. Do the same for the workouts channel.
3. Create a [Slack app](https://api.slack.com/apps) and install it to your newly created workspace.
4. On the app's homepage, go to `Basic Information`. Note the `Signing Secret` under `App Credentials`.
5. On the app's homepage, go to `OAuth & Permissions` and add the following scopes: `app_mentions:read`, `channels:history`, `channels:join`, `chat:write`, `commands`, `files:write`, `im:write`, `pins:read`, `reactions:read`, and `users:read`. Note the `Bot User OAuth Access Token`.
6. Fork this repository and create a local clone. Within your local repository run `cp expected_environment.py environment.py` to create a copy of the expected environment. This will hold your unique environmental variables. Update `ANNOUNCEMENTS_CID` and `WORKOUTS_CID` with the channel IDs from step 2, `SLACK_SIGNING_SECRET` with the `Signing Secret` from step 4, and `SLACK_BOT_TOKEN` with the `Bot User OAuth Access Token` from step 5.
7. Go to the `announcements` channel and click the "Add an app" button. Add your app.
8. On the app's homepage, go to `Slash Commands` and add the appropriate endpoints. These can be found in `./bot/slash_commands`. The base url will be generated when you run ngrok. For example, running `ngrok http 3000` might generate the base url `http://ef0eb7abb91a.ngrok.io`. In that case, the request url for the /practice command would be `http://ef0eb7abb91a.ngrok.io/slack/commands/practice`.
9. On the app's homepage, go to `Interactivity & Shortcuts`. Turn on interactivity and add the `/slack/events` endpoint. Then, add the `/slack/options-load-endpoint` under `Select Menus`.
10. Make sure python 3.8 and pip are installed on your system.
11. Install the required libraries: `pip3 install -r requirements.txt`.
12. Configure black as a pre-commit hook: `pre-commit install`.

## Running
If using localhost, you will need to use a service like ngrok to forward traffic from Slack to your events url.
Run this from the command line: `ngrok http 3000` and `python3 run.py`

## Documentation
[Slack API](https://api.slack.com)  
[Slack Python SDK](https://slack.dev/python-slackclient/)
