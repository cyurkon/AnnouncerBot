from bot import app
from bot.slash_commands.dac import update_player_table


if __name__ == "__main__":
    # Bootstrapping. Needed to satisfy the validate_request decorator
    # when calling any of the slash commands for the first time.
    with app.app_context():
        update_player_table()
    app.run(port=3000)
