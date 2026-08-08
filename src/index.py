from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

last_sender_by_channel = {}
balance = 100
#---------CODE---------

#For checking balance
@app.command("/balance-check")
def repeat_text(ack, respond):
    ack()
    respond(f"Your balance is ☭{balance}.")

#for adding to balance
@app.command("/balance-add")
def repeat_text(ack, respond, command):
    ack()
    balance += int(command['text'])
    respond(f"your new balance is ☭{balance}")

#for subtracting from balance
@app.command("/balance-subtract")
def repeat_text(ack, respond, command):
    ack()
    balance -= int(command['text'])
    respond(f"your new balance is ☭{balance}")

#For mass survellance
@app.event("message")
def handle_message_events(event, client):
    if event.get("bot_id") or event.get("subtype"):
        return

    user = event.get("user")
    channel = event.get("channel")
    if not user or not channel:
        return

    previous_user = last_sender_by_channel.get(channel)
    last_sender_by_channel[channel] = user

    if previous_user != user and previous_user is not None:
        response_text = f"You responded to <@{previous_user}> I shall now affect their social credit :devious-ahh:"

        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text=response_text
        )

#---------BOTTOM THING---------

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()