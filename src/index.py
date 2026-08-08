from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

balance = 100
#---------CODE---------

@app.command("/balance-check")
def repeat_text(ack, respond):
    ack()
    respond(f"Your balance is ${balance}.")

@app.command("/balance-add")
def repeat_text(ack, respond, command):
    ack()
    balance += int(command['text'])
    respond(f"your new balance is ${balance}")

@app.command("/balance-subtract")
def repeat_text(ack, respond, command):
    ack()
    balance -= int(command['text'])
    respond(f"your new balance is ${balance}")

#---------BOTTOM THING---------

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()