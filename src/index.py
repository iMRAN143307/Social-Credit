from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import csv
from dotenv import load_dotenv

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

last_sender_by_channel = {}


def get_display_name(client, user_id):
    if not user_id:
        return None
    user_info = client.users_info(user=user_id)
    profile = user_info.get("user", {}).get("profile", {})
    return profile.get("display_name") or profile.get("real_name") or user_id

balance = 100
#---------CODE---------

#For checking balance
@app.command("/social-credit")
def repeat_text(ack, respond, body):
    ack()
    # user = body.get("user_id")

    # user_found = False
    # try:
    #     with open('users.csv', newline='') as csvfile:
    #         reader = csv.reader(csvfile)
    #         for row in reader:
    #             if row and row[0] == user:
    #                 user_found = True
    #                 break
    # except FileNotFoundError:
    #     user_found = False
        
    # if not user_found:
    #     respond("you aren't signed up! run /social-credit-signup to sign up")
    #     return

    respond(f"Your social credit is ☭{balance} / ☭100")

# @app.command("/social-credit-signup")
# def repeat_text(ack, respond, body):
#     ack()
#     user = body.get("user_id")
#     with open('users.csv', 'a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([user])
#     respond(f"Signed up :3 you can undo this by typing /social-credit-signout")

#for adding to balance
@app.command("/social-add")
def repeat_text(ack, respond, command):
    ack()
    balance += int(command['text'])
    respond(f"your new balance is ☭{balance}")

#for subtracting from balance
@app.command("/social-subtract")
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
    message_text = event.get("text")
    channel = event.get("channel")
    if not user or not channel:
        return

    previous_user = last_sender_by_channel.get(channel)
    last_sender_by_channel[channel] = user
    previous_display_name = get_display_name(client, previous_user) if previous_user else None

    print(previous_user)

    # user_found = False
    # try:
    #     with open('users.csv', newline='') as csvfile:
    #         reader = csv.reader(csvfile)
    #         for row in reader:
    #             if row and row[0] == user:
    #                 user_found = True
    #                 break
    # except FileNotFoundError:
    #     user_found = False
    
    # if not user_found:
    #     print(f"User {user} not found in users.csv.")
    #     return

    if previous_user != user and previous_user != None:
        response_text = (f"User: {previous_user}, Display name: {previous_display_name}, Response: {message_text}")
        print(response_text)

        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([response_text])

#---------BOTTOM THING---------

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()