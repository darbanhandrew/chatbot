import frappe
import json
from chat.api.message import send

def send_bot_message(content, room_name):
    bot_email = "chatbot@taskerpage.com" # Your bot's email
    # Logic for sending a message from bot to the room
    send(
        content=content,
        user=bot_email,
        room=room_name,
        email=bot_email
    )

def echo_message(content, room_name):
    # Sends back the exact same message received
    send_bot_message(content,room_name)

def after_insert(doc, method):
    # Ensure the message is for the bot
    if not doc.action_required and not doc.chat_bot:
        return
    
    # Parse message and determine action
    if doc.action_type == "greeting":
        send_bot_message("Hello! How can I assist you today?", doc.room)
    else:
        echo_message(doc.content, doc.room)
