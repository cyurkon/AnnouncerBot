# tribeBot
Built for the Tribe B Slack Channel. Makes announcements, takes attendance, and handles other miscellaneous tasks.

## Setup
1. Create a slack app and setup slash commands and events. See bot/app.py for the specific endpoints you need. \
 If you are testing locally, install [ngrok](https://ngrok.com) to generate a base URL.
2. Save Bot User OAuth Access Token as an environmental variable under the name SLACK_BOT_TOKEN.
3. Add this bot to a test workspace.
4. Install python3 and pip on your computer.
5. Run the following commands:
`pip3 install flask slackclient`

## Running
If using localhost, you will need to use a service like ngrok to forward traffic from Slack to your events url.
Run this from the command line: `ngrok http 3000` and `python3 run.py`

## Documentation
[Slack API](https://api.slack.com)
[Slack Python SDK](https://slack.dev/python-slackclient/)
