from dotenv import load_dotenv

load_dotenv()

from bot import create_app
from bot.slash_commands.dac import update_player_table

app = create_app()
# Allows admins to call slash commands for the first time
with app.app_context():
    update_player_table()

if __name__ == "__main__":
    app.run()
