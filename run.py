from bot import app
from bot.slash_commands.upt import update_player_table


if __name__ == "__main__":
    app.run(port=3000)
    # Bootstrapping. Needed to satisfy validate_request when calling any of
    # slash commands for the first time.
    with app.app_context():
        update_player_table.unwrapped()
