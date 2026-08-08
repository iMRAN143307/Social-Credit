from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import csv
import json
import urllib.request
from dotenv import load_dotenv
from db import update_balance, get_balance
import judge

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

API_URL = os.environ.get('API_URL', 'http://127.0.0.1:5000/api/items')
DATA_CSV_PATH = os.environ.get('DATA_CSV_PATH', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data.csv')))

def post_to_api(user_id, display_name, response):
    payload = json.dumps({
        'user_id': user_id,
        'display_name': display_name,
        'response': response,
    }).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.read().decode('utf-8')
    except Exception as exc:
        print(f'Warning: failed to post to API: {exc}')
        return None

last_sender_by_channel = {}


def get_display_name(client, user_id):
    if not user_id:
        return None
    user_info = client.users_info(user=user_id)
    profile = user_info.get("user", {}).get("profile", {})
    return profile.get("display_name") or profile.get("real_name") or user_id

#---------CODE---------

# For checking balance
@app.command("/social-credit")
def social_credit(ack, respond, command, client):
    ack()
    user_id = command.get('user_id')
    display_name = get_display_name(client, user_id)
    row = get_balance(user_id)
    if not row:
        balance_value = update_balance(user_id, display_name, 0)
    else:
        balance_value = row['balance']
    respond(f"Your balance is ☭{balance_value}.")

# for adding to balance
@app.command("/social-add")
def social_add(ack, respond, command, client):
    ack()
    user_id = command.get('user_id')
    display_name = get_display_name(client, user_id)
    try:
        delta = int(command['text'])
    except Exception:
        respond("Please provide a number to add.")
        return
    balance_value = update_balance(user_id, display_name, delta)
    respond(f"your new balance is ☭{balance_value}")

# for subtracting from balance
@app.command("/social-subtract")
def social_subtract(ack, respond, command, client):
    ack()
    user_id = command.get('user_id')
    display_name = get_display_name(client, user_id)
    try:
        delta = int(command['text'])
    except Exception:
        respond("Please provide a number to subtract.")
        return
    balance_value = update_balance(user_id, display_name, -delta)
    respond(f"your new balance is ☭{balance_value}")

# For mass survellance
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

    if previous_user != user and previous_user != None:
        response_text = (f"User: {previous_user}, Display name: {previous_display_name}, Response: {message_text}")

        rows_to_write = [
            ["User", previous_user],
            ["Display name", previous_display_name],
            ["Response", message_text],
        ]
        with open(DATA_CSV_PATH, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows_to_write)

        post_result = post_to_api(previous_user, previous_display_name, message_text)
        if post_result is not None:
            print('Posted to API:', post_result)

        judge_result = judge.process_response(previous_user, message_text, previous_display_name)
        if judge_result is not None:
            print(f"Judge updated balance: {judge_result}")

#---------BOTTOM THING---------

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()