# tribeBot
Built for the Tribe B Slack Channel. Makes announcements, takes attendance, and handles other miscellaneous tasks.

## Setup
1. Visit and install [ngrok](https://ngrok.com/download) if you plan to test locally (recommended). After getting the package all you need to do is unzip it. Its recommended you add this to your PATH variable so you can access the ngrok command from anywhere.
2. Create a new slack workspace that you can use to test in.
3. Create a [slack app](https://api.slack.com/apps) and link it to your newly created workspace.
4. Go to 'App Home' from the side panel and update the Oauth stuff. These are the permissions for the bot. General read and write stuff are what you will need.
5. Create your OAuth access token on this page. Copy this token. Then within your local repo run `cp expected_environment.py environment.py` to create a copy of the expected environment. This will hold our environment variables which are keys. These are unique to our individual environments (most of the time). Update SLACK_BOT_TOKEN with the copied token.
6. Go to 'Slash Commands' from the side panel in the slack app and add the appropriate endpoints. These are in `./bot/app.py`. The base url will be generated when you run ngrok. For example, running `ngrok http 3000` will show a base url of 'http://ef0eb7abb91a.ngrok.io', so my full url for a command would be something like 'http://ef0eb7abb91a.ngrok.io/slack/practice'
7. Go to 'Interactivity & Shortcuts' and add the `/slack/events` endpoint. This should be added here and not in the slash commands.
8. Make sure python3 and pip are installed on your system.
9. Make sure flask and slackclient are installed for the project: `pip3 install flask slackclient black pre-commit`

## Running
If using localhost, you will need to use a service like ngrok to forward traffic from Slack to your events url.
Run this from the command line: `ngrok http 3000` and `python3 run.py`

## Documentation
[Slack API](https://api.slack.com)
[Slack Python SDK](https://slack.dev/python-slackclient/)
