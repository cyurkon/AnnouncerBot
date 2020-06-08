# AnnouncerBot
Built for the Tribe B Slack Channel
## Setup
1. Create a slack app and setup the correct endpoints for slash commands and events.
2. Save SLACK_BOT_TOKEN as an environmental variable
2. Install python3 and pip on your computer
3. Run the following commands:   
`pip3 install flask` 


## Running
If using localhost, you will need to use a service like ngrok to forward traffic from Slack to your events url.
Run this from the command line: 'ngrok http 3000'  'python3 run.py'
