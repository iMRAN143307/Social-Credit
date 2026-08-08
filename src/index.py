from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
def handle_mention(event, say, logger):
    print(f"App mentioned by user: {event['user']}")
    logger.info(f"App mentioned by user: {event['user']}")
    say(f"Hi <@{event['user']}>!")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
    print("Running!")